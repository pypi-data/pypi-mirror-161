import enum
import time
from kabaret import flow
from kabaret.flow_entities.entities import Entity, Property

from ..utils.kabaret.flow_entities.entities import EntityView

from .file import FileSystemMap
from .maputils import SimpleCreateAction
from .task_manager import CreateTaskDefaultFiles, ManageTasksAction


class IconSize(enum.Enum):

    SMALL  = 0
    MEDIUM = 1
    LARGE  = 2


class Task(Entity):
    """
    Defines an arbitrary task containing a list of files.

    Instances provide the `task` and `task_display_name` keys
    in their contextual dictionary (`settings` context).
    """
    
    display_name = Property().ui(hidden=True)
    enabled      = Property().ui(hidden=True, editor='bool')
    icon_small   = Property().ui(hidden=True)
    icon_medium  = Property().ui(hidden=True)
    icon_large   = Property().ui(hidden=True)

    files = flow.Child(FileSystemMap).ui(
        expanded=True,
        action_submenus=True,
        items_action_submenus=True
    )

    @classmethod
    def get_source_display(cls, oid):
        split = oid.split('/')
        return f'{split[3]} · {split[5]} · {split[7]} · {split[9]}'
    
    def get_default_contextual_edits(self, context_name):
        if context_name == 'settings':
            return dict(
                task=self.name(),
                task_display_name=self.display_name.get(),
            )
    
    def get_icon(self, size=IconSize.SMALL):
        if size == IconSize.SMALL:
            return self.icon_small.get()
        elif size == IconSize.MEDIUM:
            return self.icon_medium.get()
        else:
            return self.icon_large.get()


class TaskCollection(EntityView):
    """
    Defines a collection of tasks.
    """

    add_task = flow.Child(SimpleCreateAction)

    @classmethod
    def mapped_type(cls):
        return flow.injection.injectable(Task)
    
    def collection_name(self):
        mgr = self.root().project().get_entity_manager()
        return mgr.get_task_collection().collection_name()


# Managed tasks
# -------------------------


class ProjectUserNames(flow.values.SessionValue):

    DEFAULT_EDITOR = 'choice'

    STRICT_CHOICES = False

    _task = flow.Parent(2)

    def choices(self):
        users = set(self.root().project().get_users().mapped_names())
        assigned_users = set(self._task.assigned_users.get())
        
        return list(users - assigned_users)
    
    def revert_to_default(self):
        names = self.choices()
        if names:
            self.set(names[0])


class SubtaskNames(flow.values.SessionValue):

    DEFAULT_EDITOR = 'multichoice'

    STRICT_CHOICES = False

    _action = flow.Parent()
    _task = flow.Parent(2)

    def choices(self):
        tm = self.root().project().get_task_manager()
        return tm.get_subtasks(self._task.name())
    
    def update_assigned_tasks(self):
        assigned_subtasks = self._task.get_assigned_subtasks(
            self._action.user.get()
        )
        self.set(assigned_subtasks)


class EditUserAssignations(flow.Action):

    user     = flow.SessionParam(value_type=ProjectUserNames).watched()
    subtasks = flow.SessionParam(list, value_type=SubtaskNames)

    _task = flow.Parent()

    def needs_dialog(self):
        self.user.revert_to_default()
        self.subtasks.update_assigned_tasks()
        return True
    
    def get_buttons(self):
        return ['Save', 'Close']
    
    def run(self, button):
        if button == 'Close':
            return
        
        assigned = set(self.subtasks.get())
        unassigned = set(self.subtasks.choices()) - assigned

        for st in assigned:
            self._task.assign_users(self.user.get(), subtask_name=st)
        for st in unassigned:
            self._task.unassign_users(self.user.get(), subtask_name=st)
        
        return self.get_result(close=False)
    
    def child_value_changed(self, child_value):
        if child_value is self.user:
            self.subtasks.update_assigned_tasks()


class ManagedTask(Task):
    """
    A ManagedTask provides features handled by the task
    manager of the project.
    """

    assigned_users         = Property().ui(hidden=True)
    subtask_assigned_users = Property().ui(hidden=True)
    current_subtask        = Property().ui(hidden=True)
    
    create_dft_files = flow.Child(CreateTaskDefaultFiles).ui(
        label='Create default files'
    )

    edit_assignations = flow.Child(EditUserAssignations)

    def is_assigned(self, user_name, subtask_name=None):
        assigned_users = self._get_assigned_users(subtask_name)
        assigned = user_name in assigned_users

        if subtask_name is None and not assigned:
            # If not explicitly assigned to the task, check if user is assigned to one of its subtasks
            st_assigned_users = self.subtask_assigned_users.get() or {}
            assigned |= user_name in set().union(*st_assigned_users.values())
        
        return assigned

    def assign_users(self, *user_names, subtask_name=None):
        names = set(self._get_assigned_users(subtask_name))
        names |= set(user_names)
        self._set_assigned_users(list(names), subtask_name)

    def unassign_users(self, *user_names, subtask_name=None):
        names = set(self._get_assigned_users(subtask_name))
        names -= set(user_names)
        self._set_assigned_users(list(names), subtask_name)
    
    def get_assigned_subtasks(self, user_name):
        assigned_users = self.subtask_assigned_users.get() or {}
        return [
            st for st, user_names in assigned_users.items()
            if user_name in user_names
        ]
    
    def _get_assigned_users(self, subtask_name=None):
        if subtask_name is None:
            names = self.assigned_users.get() or []
        else:
            assigned_users = self.subtask_assigned_users.get() or {}
            names = assigned_users.get(subtask_name, [])
        
        return names
    
    def _set_assigned_users(self, user_names, subtask_name=None):
        if subtask_name is None:
            self.assigned_users.set(user_names)
        else:
            assigned_users = self.subtask_assigned_users.get() or {}
            assigned_users[subtask_name] = user_names
            self.subtask_assigned_users.set(assigned_users)


class ManagedTaskCollection(TaskCollection):

    manage_tasks = flow.Child(ManageTasksAction).injectable().ui(
        label='Manage tasks'
    )

    @classmethod
    def mapped_type(cls):
        return flow.injection.injectable(ManagedTask)
    
    def mapped_names(self, page_num=0, page_size=None):
        names = super(ManagedTaskCollection, self).mapped_names(
            page_num, page_size
        )
        # Sort tasks by their positions configured in the project's default tasks
        default_tasks = {
            dt.name(): dt
            for dt in self.get_default_tasks()
        }
        names = sorted(
            names,
            key=lambda n: default_tasks[n].position.get()
        )
        return names
    
    def get_default_tasks(self):
        tm = self.root().project().get_task_manager()
        return tm.default_tasks.mapped_items()
    
    def _fill_row_cells(self, row, item):
        mgr = self.root().project().get_task_manager()
        row['Name'] = mgr.get_task_display_name(item.name())

    def _fill_row_style(self, style, item, row):
        mgr = self.root().project().get_task_manager()
        user_name = self.root().project().get_user_name()

        style['icon'] = mgr.get_task_icon(item.name())

        if (
            mgr.is_assignation_enabled(item.name())
            and not item.is_assigned(user_name)
        ):
            color = '#4e5255'
        else:
            color = mgr.get_task_color(item.name())
        
        style['foreground-color'] = color
