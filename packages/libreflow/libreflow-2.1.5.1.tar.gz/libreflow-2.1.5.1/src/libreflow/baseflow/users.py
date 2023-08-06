import os
import json
import getpass
import fnmatch

from kabaret import flow


class MyBookmarks(flow.DynamicMap):

    def mapped_names(self, page_num=0, page_size=None):
        user = self.root().project().get_user()
        if user is not None:
            return user.bookmarks.mapped_names()
        else:
            return []

    @classmethod
    def mapped_type(cls):
        return flow.injection.injectable(Bookmark)

    def columns(self):
        return ["Bookmark"]

    def _fill_row_cells(self, row, item):
        name = item.name()
        bookmarks = self.root().project().get_user().bookmarks
        oid = bookmarks[name].goto_oid.get()
        objects = (
            self.root()
            .session()
            .cmds.Flow.split_oid(oid, up_to_oid=self.root().project().oid())
        )
        object_names = [obj[0].split(":")[-1] for obj in objects]

        row["Bookmark"] = " > ".join(object_names)

    def _fill_row_style(self, style, item, row):
        name = item.name()
        bookmarks = self.root().project().get_user().bookmarks
        oid = bookmarks[name].goto.oid()
        style["activate_oid"] = oid
    
    def _fill_ui(self, ui):
        super(MyBookmarks, self)._fill_ui(ui)
        ui['hidden'] = self.root().project().get_user() is None


class GotoPreferences(flow.Action):

    _profile = flow.Parent()

    def allow_context(self, context):
        user = self.root().project().get_user(
            self._profile.current_user_id.get()
        )
        return (
            context
            and context.endswith('.inline')
            and user is not None
        )

    def needs_dialog(self):
        return False
    
    def run(self, button):
        user_pref_oid = '/'.join([
            self.root().project().admin.users.oid(),
            self._profile.current_user_id.get(),
            'preferences'
        ])
        return self.get_result(goto=user_pref_oid)
    

class UserProfile(flow.Object):
    '''
    This part is made for the user
    '''

    ICON = ('icons.gui', 'user')

    current_user_id = flow.Computed(cached=True)
    my_bookmarks = flow.Child(MyBookmarks).ui(expanded=True)
    preferences = flow.Child(GotoPreferences)

    def compute_child_value(self, child_value):
        if child_value is self.current_user_id:
            # Check env
            if "USER_NAME" in os.environ:
                child_value.set(os.environ["USER_NAME"])
                return
            
            # Check user file
            current_user_file = os.path.join(
                self.root().project().project_settings_folder(),
                "current_user.json"
            )
            if os.path.exists(current_user_file):
                with open(current_user_file, "r") as f:
                    user_config = json.load(f)
                    child_value.set(user_config["username"])
                    return

            # Return local user name otherwise
            child_value.set(getpass.getuser())
    
    def summary(self):
        user = self.root().project().get_user(self.current_user_id.get())
        if user is None:
            return (
                '<font color=#D5000D>User '
                f'<b>{self.current_user_id.get()}</b>'
                ' undefined.</font>'
            )

    def _fill_ui(self, ui):
        if self.root().project().show_login_page():
            ui["custom_page"] = "libreflow.baseflow.LoginPageWidget"




###################################################
# This part is still users, but from an admin POV #
###################################################



class GotoBookmarkAction(flow.Action):

    _bookmark = flow.Parent()

    def needs_dialog(self):
        return False

    def run(self, button):
        # This is overkill, but needed to the dynamicMap can use the same actions
        bookmarks = self.root().project().get_user().bookmarks
        return self.get_result(goto=bookmarks[self._bookmark.name()].goto_oid.get())


class RemoveFromBookmark(flow.Action):

    _bookmark = flow.Parent()
    _bookmarks = flow.Parent(2)

    def needs_dialog(self):
        return False

    def run(self, button):
        # This is overkill, but needed to the dynamicMap can use the same actions
        bookmarks = self.root().project().get_user().bookmarks
        bookmarks.remove_bookmark(self._bookmark.name())
        self._bookmarks.touch()


class Bookmark(flow.values.Value):
    goto_oid = flow.Param()
    remove = flow.Child(RemoveFromBookmark)
    goto = flow.Child(GotoBookmarkAction)


class ToggleBookmarkAction(flow.Action):

    _obj = flow.Parent()

    def needs_dialog(self):
        return False

    def allow_context(self, context):
        return context and context.endswith(".details")

    def get_bookmarks(self):
        return self.root().project().get_user().bookmarks

    def is_bookmarked(self):
        return self.get_bookmarks().has_bookmark(self._obj.oid())

    def run(self, button):
        bookmarks = self.get_bookmarks()

        if self.is_bookmarked():
            self.root().session().log_debug("Remove %s to bookmarks" % self._obj.oid())
            bookmarks.remove_bookmark(self._obj.oid())
        else:
            self.root().session().log_debug("Add %s to bookmarks" % self._obj.oid())
            bookmarks.add_bookmark(self._obj.oid())
        # Ideally this touch is needed, but we can save some of them
        # bookmarks.touch()
        self.root().project().user.my_bookmarks.touch()
        return self.get_result(refresh=True)

    def _fill_ui(self, ui):
        ui["label"] = ""

        if self.is_bookmarked():
            ui["icon"] = ("icons.gui", "star")
        else:
            ui["icon"] = ("icons.gui", "star-1")


class UserBookmarks(flow.Map):
    '''
    This is the actual map where we store
    the user's bookmarks, based on its existance
    in the Users maps
    '''

    @classmethod
    def mapped_type(cls):
        return Bookmark

    def _fill_row_cells(self, row, item):
        oid = item.goto_oid.get()
        objects = (
            self.root()
            .session()
            .cmds.Flow.split_oid(oid, up_to_oid=self.root().project().oid())
        )
        object_names = [obj[0].split(":")[-1] for obj in objects]

        row["Bookmark"] = " > ".join(object_names)
    
    def columns(self):
         return ["Bookmark"]
    
    def has_bookmark(self, oid):
        if "/" in oid:
            name = oid[1:].replace("/", "_")
        else:
            name = oid
        return True if name in self.mapped_names() else False

    def add_bookmark(self, oid):
        name = oid[1:].replace("/", "_")
        bookmark = self.add(name)
        bookmark.goto_oid.set(oid)
        self.touch()

    def remove_bookmark(self, oid):
        if "/" in oid:
            name = oid[1:].replace("/", "_")
        else:
            name = oid
        if self.has_bookmark(name):
            self[name].goto_oid.revert_to_default()
            self.remove(name)
        self.touch()

    def _fill_row_style(self, style, item, row):
        style["activate_oid"] = item.goto.oid()


class PresetValueManager(flow.Object):

    _value = flow.Parent()


class PresetValue(flow.values.Value):

    def get_preset(self):
        return self._get_presets().get_preset(self.oid())
    
    def apply_preset(self):
        preset = self.get_preset()

        if preset is not None:
            self.set(preset)
        else:
            self.revert_to_default()
    
    def update_preset(self):
        presets = self._get_presets()
        presets.update_preset(self.oid(), self.get())
    
    def _get_presets(self):
        user = self.root().project().get_user()
        return user.preferences.option_presets


class PresetChoiceValue(PresetValue):

    def apply_preset(self):
        preset = self.get_preset()

        if preset is not None and preset in self.choices():
            self.set(preset)
        else:
            self.revert_to_default()


class PresetSessionValue(flow.values.SessionValue):

    def get_preset(self):
        return self._get_presets().get_preset(self.oid())

    def apply_preset(self):
        preset = self.get_preset()

        if preset is not None:
            self.set(preset)
    
    def update_preset(self):
        presets = self._get_presets()
        presets.update_preset(self.oid(), self.get())
    
    def _get_presets(self):
        user = self.root().project().get_user()
        return user.preferences.option_presets


class OptionPreset(flow.Object):

    contexts = flow.OrderedStringSetParam()
    context_values = flow.DictParam({})
    default_value = flow.Param()


class BoolOptionPreset(OptionPreset):

    default_value = flow.BoolParam()


class OptionPresets(flow.Map):

    @classmethod
    def mapped_type(cls):
        return OptionPreset
    
    def get_preset(self, param_oid):
        param_context, param_name = param_oid.rsplit('/', maxsplit=1)
        value = None

        if self.has_mapped_name(param_name):
            preset = self.get_mapped(param_name)
            context_values = preset.context_values.get()

            if not context_values:
                value = preset.default_value.get()
            else:
                for context in preset.contexts.get():
                    if fnmatch.fnmatch(param_context, context):
                        return context_values[context]
                
                # No contextual preset defined or matching the given param context
                value = preset.default_value.get()
        
        return value
    
    def update_preset(self, param_oid, value):
        param_context, param_name = param_oid.rsplit('/', maxsplit=1)

        if not self.has_mapped_name(param_name):
            ui = self.root().session().cmds.Flow.get_object_ui(param_oid)
            
            if ui.get('editor_type', None) == 'bool':
                preset = self.add_bool_preset(param_name)
            else:
                preset = self.add(param_name)
        else:
            preset = self.get_mapped(param_name)
            context_values = preset.context_values.get()

            if not context_values:
                preset.default_value.set(value)
                return
            else:
                for context in preset.contexts.get():
                    if fnmatch.fnmatch(param_context, context):
                        context_values[context] = value
                        preset.context_values.set(context_values)
                        return
        
        # No contextual preset defined or matching the given param context
        preset.default_value.set(value)
    
    def add_bool_preset(self, name):
        return super(OptionPresets, self).add(name, object_type=BoolOptionPreset)


class UserPreferences(flow.Object):

    create_working_copies = flow.BoolParam(False)
    option_presets = flow.Child(OptionPresets)


class UserStatus(flow.values.ChoiceValue):

    CHOICES = ["User", "Admin", "Supervisor"]


class SessionUserStatus(flow.values.SessionValue):

    DEFAULT_EDITOR = 'choice'

    def choices(self):
        return ["User", "Admin", "Supervisor"]


class AddUserAction(flow.Action):

    ICON = ("icons.gui", "plus-sign-in-a-black-circle")

    _users = flow.Parent()

    user_id = flow.SessionParam("").ui(label="ID")
    login   = flow.SessionParam("")
    status  = flow.SessionParam("User", SessionUserStatus)

    def get_buttons(self):
        return ["Add", "Cancel"]

    def run(self, button):
        if button == "Cancel":
            return

        user = self._users.add_user(
            self.user_id.get(),
            self.login.get(),
            self.status.get()
        )
        self._users.touch()


class User(flow.Object):

    ICON = ("icons.gui", "user")

    login  = flow.Param().watched()
    status = flow.Param("User", UserStatus).ui(editable=False)

    bookmarks = flow.Child(UserBookmarks)
    preferences = flow.Child(UserPreferences)

    _map = flow.Parent()

    def child_value_changed(self, child_value):
        if child_value is self.login:
            self._map.set_user_login(self.name(), self.login.get())


class Users(flow.Map):

    ICON = ("icons.gui", "team")
    STYLE_BY_STATUS = {
        'User': ('icons.gui', 'user'),
        'Admin': ('icons.gui', 'user-admin'),
        'Supervisor': ('icons.gui', 'user-lead')
    }

    add_user_action = flow.Child(AddUserAction).ui(label="Add user")

    _name_by_uid = flow.HashParam()
    _mapped_name_per_login = flow.HashParam() # Allow to retrieve users by their logins

    @classmethod
    def mapped_type(cls):
        return flow.injection.injectable(User)

    def columns(self):
        return ['ID', 'Login']

    def is_admin(self, username):
        user = self.get_mapped(username)
        return user.status.get() == "Admin"
    
    def add_user(self, name, login, status='User'):
        user = self.add(name)
        user.status.set(status)
        user.login.set(login)
        self.set_user_login(name, login)

        return user
    
    def remove_user(self, name):
        self.remove(name)
        self._mapped_name_per_login.del_key(name)
    
    def get_user(self, login):
        if not self._mapped_name_per_login.has_key(login):
            return None
        
        name = self._mapped_name_per_login.get_key(login)
        return self.get_mapped(name)
    
    def set_user_login(self, mapped_name, login):
        u = self.get_mapped(mapped_name)
        self._mapped_name_per_login.set_key(login, mapped_name)

    def _fill_row_cells(self, row, item):
        row["ID"] = item.name()
        row["Login"] = item.login.get()
    
    def _fill_row_style(self, style, item, row):
        style['icon'] = self.STYLE_BY_STATUS[item.status.get()]


class AddEnvVarAction(flow.Action):

    _env = flow.Parent()

    var_name = flow.SessionParam("").ui(label="Name")
    var_value = flow.SessionParam("").ui(label="Value")

    def get_buttons(self):
        return ["Add", "Cancel"]

    def run(self, button):
        if button == "Cancel":
            return

        if self.var_name.get() == "":
            self.message.get("<font color=#D50055>Variable name can't be empty</font>")
            return self.get_result(close=False)

        env_path = self._env.file_path()

        try:
            f = open(env_path, "r")
        except IOError:
            f = open(env_path, "w")
            env = {self.var_name.get(): self.var_value.get()}
        else:
            try:
                env = json.load(f)
            except json.decoder.JSONDecodeError:
                env = {self.var_name.get(): self.var_value.get()}
            else:
                env[self.var_name.get()] = self.var_value.get()

            f = open(env_path, "w")

        json.dump(env, f, indent=4, sort_keys=True)
        f.close()

        #os.environ[self.var_name.get()] = self.var_value.get()
        self._env.touch()
        self.var_name.revert_to_default()
        self.var_value.revert_to_default()


class ChangeEnvVarValueAction(flow.Action):

    _var = flow.Parent()
    _env = flow.Parent(2)

    var_value = flow.Param("").ui(label="Value")

    def get_buttons(self):
        return ["Confirm", "Cancel"]

    def run(self, button):
        if button == "Cancel":
            return

        env_path = self._env.file_path()

        try:
            f = open(env_path, "r")
        except IOError:
            return

        env = json.load(f)
        env[self._var.name()] = self.var_value.get()

        f = open(env_path, "w")
        json.dump(env, f, indent=4, sort_keys=True)
        f.close()

        self._var.set(self.var_value.get())
        self._var.update()


class EnvVar(flow.values.SessionValue):

    change_value = flow.Child(ChangeEnvVarValueAction)

    def update(self):
        pass
        #os.environ[self.name()] = self.get()


class UserEnvironment(flow.DynamicMap):

    add_variable = flow.Child(AddEnvVarAction)

    @classmethod
    def mapped_type(cls):
        return EnvVar

    def mapped_names(self, page_num=0, page_size=None):
        try:
            f = open(self.file_path(), "r")
        except IOError:
            return []

        try:
            env = json.load(f)
        except json.decoder.JSONDecodeError:
            # Invalid JSON object
            return []

        return env.keys()

    def file_path(self):
        return "%s/env.json" % self.root().project().user_settings_folder()

    def _configure_child(self, child):
        with open(self.file_path(), "r") as f:
            env = json.load(f)
            child.set(env[child.name()])

    def update(self):
        for var in self.mapped_items():
            var.update()

    def columns(self):
        return ["Variable", "Value"]

    def _fill_row_cells(self, row, item):
        row["Variable"] = item.name()
        row["Value"] = item.get()

    def _fill_row_style(self, style, item, row):
        style["activate_oid"] = item.change_value.oid()



