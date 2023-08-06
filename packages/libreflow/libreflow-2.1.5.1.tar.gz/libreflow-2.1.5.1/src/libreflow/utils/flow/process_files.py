from kabaret import flow
from kabaret.flow_contextual_dict import get_contextual_dict
from libreflow.baseflow.file import GenericRunAction


class SequenceFillerChoiceValue(flow.values.SessionValue):

    DEFAULT_EDITOR = 'choice'
    CHOICES = ['Nothing', 'Black', 'Magenta', 'SMPTE Bars']

    _action = flow.Parent()

    def choices(self):
        return self.CHOICES
    
    def revert_to_default(self):
        value = self.root().project().get_action_value_store().get_action_value(
            self._action.name(),
            self.name(),
        )

        if value in self.choices():
            self.set(value)


class SequenceSessionValue(flow.values.SessionValue):

    _action = flow.Parent()
   
    def revert_to_default(self):
        value = self.root().project().get_action_value_store().get_action_value(
            self._action.name(),
            self.name(),
        )
        self.set(value)


class PlaySequenceAction(GenericRunAction):

    ICON = ('icons.gui', 'chevron-sign-to-right')

    _sequence = flow.Parent()

    filler_type      = flow.SessionParam('', SequenceFillerChoiceValue).ui(hidden=True)
    duration_seconds = flow.SessionParam(1, SequenceSessionValue).ui(hidden=True)
    priority_files   = flow.SessionParam([], SequenceSessionValue).ui(hidden=True)
   
    def __init__(self, parent, name):
        super(PlaySequenceAction, self).__init__(parent, name)
        self._paths = []
        self.status = None

    def needs_dialog(self):
        self.filler_type.revert_to_default()
        self.duration_seconds.revert_to_default()
        self.priority_files.revert_to_default()
        self.status = self.get_files()

        if self.status == 'Nothing' or self.filler_type.get() == '':
            return True
        return False

    def get_buttons(self):
        if self.status == 'Nothing':
            self.message.set('<h2>No files has been found.</h2>')
        elif self.filler_type.get() == '':
            self.message.set('<h2>Incorrect filler type.</h2>')
        return ['Close']
    
    def runner_name_and_tags(self):
        return 'RV', []
    
    def get_version(self, button):
        return None
          
    def extra_argv(self):
        return ['-autoRetime', '0'] + self._paths
    
    def run(self, button):
        if button == 'Close':
            return

        width = get_contextual_dict(self, 'settings').get(
            'width', 1920
        )
        height = get_contextual_dict(self, 'settings').get(
            'height', 1080
        )
        fps = get_contextual_dict(self, 'settings').get(
            'fps', 24
        )
        frames = self.duration_seconds.get() * fps
        
        if self.filler_type.get() == 'Nothing':
            paths = [path for path in self._paths if path != 'None']
            self._paths = paths
        else:
            if self.filler_type.get() == 'Black':
                filler = 'solid,red=0,green=0,blue=0'
            elif self.filler_type.get() == 'Magenta':
                filler = 'solid,red=1,green=0,blue=1'
            elif self.filler_type.get() == 'SMPTE Bars':
                filler = 'smptebars'
                
            args = '{filler},width={width},height={height},start=1,end={frames},fps={fps}.movieproc'.format(
                filler=filler,
                width=width,
                height=height,
                frames=frames,
                fps=fps
            )
            paths = [path.replace('None', args) for path in self._paths]
            self._paths = paths
        
        super(PlaySequenceAction, self).run(button)
        return self.get_result(close=True)
    
    def get_files(self):
        self._paths = []
       
        for shot in self._sequence.shots.mapped_items():
            path = 'None'
            
            for priority_file in self.priority_files.get():
                task, file_name = priority_file.rsplit('/', 1)
                name, ext = file_name.rsplit('.', 1)

                if shot.tasks[task].files.has_file(name, ext):
                    revision = shot.tasks[task].files[f'{name}_{ext}'].get_head_revision(sync_status='Available')
                    path = revision.get_path()
                    break
            
            self._paths += [path]
        
        if all('None' in path for path in self._paths):
            return 'Nothing'
