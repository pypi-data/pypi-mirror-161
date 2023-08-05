from fnmatch import fnmatch
from kabaret import flow


class ProcessSequenceFiles(flow.Action):

    _sequence = flow.Parent()

    def __init__(self, parent, name):
        super(ProcessSequenceFiles, self).__init__(parent, name)
        self._files_data = None
        self._task_names = []
    
    def ensure_files_data(self):
        '''
        Method used to cache computed files data
        '''
        if self._files_data is None:
            self._files_data = self._compute_files_data()
        
        return self._files_data
    
    def _compute_files_data(self):
        '''
        Computes data related to files contained in a sequence
        '''
        raise NotImplementedError(
            'Subclasses must return shot files data'
        )
    
    def get_shot_task_files(self, fnpatterns, tags=[]):
        self._task_names.clear()
        
        template = self.root().project().admin.dependency_templates['shot']
        default_dep_names = template.get_default_dependency_names()
        dependencies = template.get_dependencies()
        
        template_tasks_files = []
        
        for dep_name in default_dep_names:
            dep = dependencies[dep_name]
            files = []
            
            for file_name, file_data in dep['files'].items():
                file_tags = file_data.get('tags', [])
                
                if not file_tags and tags:
                    continue
                if not set(tags).issubset(set(file_tags)):
                    continue
                        
                for pattern in fnpatterns:
                    if fnmatch(file_name, pattern):
                        files.append((file_name, file_data))
            
            if files:
                template_tasks_files.append((
                    dep_name,
                    files
                ))
                self._task_names.append(dep_name)
        
        return template_tasks_files
    
    def get_shot_task_names(self):
        self.ensure_files_data()
        return self._task_names