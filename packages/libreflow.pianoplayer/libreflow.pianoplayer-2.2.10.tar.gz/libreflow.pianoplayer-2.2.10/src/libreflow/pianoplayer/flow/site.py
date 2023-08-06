import os
import platform
from kabaret import flow
from libreflow.baseflow.site import WorkingSite as BaseWorkingSite
from libreflow.baseflow.site import ConfigureWorkingSite as BaseConfigureWorkingSite
from libreflow.utils.flow import SiteActionView

class ConfigureWorkingSite(BaseConfigureWorkingSite):
    use_sg_default = flow.BoolParam(True).ui(label="Use ShotGrid Default Account")

    with flow.group('ShotGrid Login'):
        sg_login = flow.Param("").ui(label="Login")
        sg_password = flow.Param("").ui(label="Password", editor='password')
    
    def _fill_action_fields(self):
        self.use_sg_default.set(self._site.use_sg_default.get())
        self.sg_login.set(self._site.sg_login.get())
        self.sg_password.set(self._site.sg_password.get())
        super(ConfigureWorkingSite, self)._fill_action_fields()
    
    def _configure_site(self, site):
        site.use_sg_default.set(self.use_sg_default.get())
        site.sg_login.set(self.sg_login.get())
        site.sg_password.set(self.sg_password.get())
        super(ConfigureWorkingSite, self)._configure_site(site)
    
    def run(self, button):
        if self.use_sg_default.get():
            self.sg_login.set("")
            self.sg_password.set("")
        super(ConfigureWorkingSite, self).run(button)

class SGEditable(flow.values.StringValue):
    _site = flow.Parent()

    def _fill_ui(self, ui):
        ui['editable'] = self._site.sg_editable.get()


class EditMultiOSValue(flow.Action):

    environ_var_name = flow.Param()
    value_windows    = flow.SessionParam()
    value_linux      = flow.SessionParam()
    value_darwin     = flow.SessionParam()

    _value = flow.Parent()

    def get_buttons(self):
        self._update_values()
        return ['Save', 'Cancel']
    
    def _update_values(self):
        self.environ_var_name.set(self._value.environ_var_name.get())
        self.value_windows.set(self._value.value_windows.get())
        self.value_linux.set(self._value.value_linux.get())
        self.value_darwin.set(self._value.value_darwin.get())
    
    def run(self, button):
        if button == 'Cancel':
            return
        
        self._value.environ_var_name.set(self.environ_var_name.get())
        self._value.value_windows.set(self.value_windows.get())
        self._value.value_linux.set(self.value_linux.get())
        self._value.value_darwin.set(self.value_darwin.get())
        self._value.touch()


class MultiOSValue(flow.values.ComputedValue):
    '''
    Defines a value which computes itself according to the
    value of the environment variable `environ_var_name`, if
    defined, or the values specified in the three following
    parameters depending on the currently running OS.
    '''

    environ_var_name = flow.Param()
    value_windows    = flow.Param()
    value_linux      = flow.Param()
    value_darwin     = flow.Param()

    edit = flow.Child(EditMultiOSValue)

    def compute(self):
        # Use value to store environment variable name
        env_var = self.environ_var_name.get()
        value = None

        if env_var is not None and env_var in os.environ:
            value = os.environ[env_var]
        else:
            # Get the operative system
            _os = platform.system()
            if _os == 'Windows':
                value = self.value_windows.get()
            elif _os == 'Linux':
                value = self.value_linux.get()
            elif _os == 'Darwin':
                value = self.value_darwin.get()
            else:
                raise Exception(
                    f'ERROR: Unrecognised OS to get {self.oid()} value'
                )
        
        self.set(value)


class MultiOSParam(flow.Computed):

    _DEFAULT_VALUE_TYPE = MultiOSValue


class WorkingSite(BaseWorkingSite):

    configuration = flow.Child(ConfigureWorkingSite)

    use_sg_default = flow.BoolParam().ui(label="Use ShotGrid Default Account", editable=False)

    with flow.group('ShotGrid Login'):
        sg_editable = flow.BoolParam().ui(hidden=True, label="Is Editable").watched()
        sg_login = flow.Param("", SGEditable).ui(hidden=True)
        sg_password = flow.Param("", SGEditable).ui(editor='password', hidden=True)
        sg_displaylogin = flow.Computed().ui(label="Login")
        sg_displaypassword = flow.Computed().ui(label="Password", editor='password')

    actions = flow.Child(SiteActionView)

    package_target_dir = MultiOSParam()
    package_layout_dir = MultiOSParam()
    package_clean_dir  = MultiOSParam()
    export_target_dir  = MultiOSParam()
    target_sites       = flow.OrderedStringSetParam()

    def compute_child_value(self, child_value):
        if child_value is self.sg_displaylogin:
            if self.use_sg_default.get() == True:
                self.sg_login.set(self.root().project().admin.project_settings.sg_login.get())
            self.sg_displaylogin.set(self.sg_login.get())
        elif child_value is self.sg_displaypassword:
            if self.use_sg_default.get() == True:
                self.sg_password.set(self.root().project().admin.project_settings.sg_password.get())
            self.sg_displaypassword.set(self.sg_password.get())
        super(WorkingSite, self).compute_child_value(child_value)