from gettext import gettext as _
from gi.repository import GObject, Gio, Gtk, Gedit, GtkSource
import os.path

# Puts a "Open From Template" menu item into the file menu
ui_str = """
<ui>
  <menubar name="MenuBar">
    <menu name="FileMenu" action="File">
      <placeholder name="FileOps_2">
        <separator/>
        <menuitem name="FileOpenFromTemplate" action="open_from_template"/>
      </placeholder>
    </menu>
  </menubar>
</ui>
"""

class TemplatePlugin(GObject.Object, Gedit.WindowActivatable):
	__gtype_name__ = "TemplatePlugin"

	window = GObject.property(type=Gedit.Window)

	def __init__(self):
		GObject.Object.__init__(self)
        
	def do_activate(self):
		# Insert menu items
		self._insert_menu()
		
	def do_deactivate(self):
        # Remove any installed menu items
		self._remove_menu()
		self._action_group = None
		
	def _insert_menu(self):
		# Get the GtkUIManager
		manager = self.window.get_ui_manager()

		# Create a new action group
		self._action_group = Gtk.ActionGroup("OpenFromTemplateActions")
		self._action_group.add_actions([("open_from_template", None, _("New From Template"),
				                              "<control>t", _("Create a new file based on a custom defined template"),
				                              self.on_open_from_template_activate)], self.window)

		# Insert the action group
		manager.insert_action_group(self._action_group)

		# Merge the UI
		self._ui_id = manager.add_ui_from_string(ui_str)

	def _remove_menu(self):
		# Get the GtkUIManager
		manager = self.window.get_ui_manager()
		
		# Remove the ui
		manager.remove_ui(self._ui_id)
		
		# Remove the action group
		manager.remove_action_group(self._action_group)
		
		# Make sure the manager updates
		manager.ensure_update()

	def do_update_state(self):
		pass
        
    # Menu activate handlers.
	# 1. provide a file chooser dialog
	#		chooser = Gtk.FileChooserDialog("Choose Template File",action=Gtk.FILE_CHOOSER_ACTION_OPEN,buttons=(Gtk.STOCK_CANCEL,Gtk.RESPONSE_CANCEL,Gtk.STOCK_OPEN,Gtk.RESPONSE_OK))
	# 2. parse the file chosen and extract all $$.*$$ strings
	# 3. construct a dialog that displays the extracted vars and a text entry
	# 4. write the new file to a new blank document.
	#		new_tab = self.window.create_tab(True)
	#		doc = new_tab.get_document()
	#		doc.set_text(parsed_text)
	def on_open_from_template_activate(self, action, window):
		# create and display a file chooser dialog
		this_title = "Open Template File..."
		homedir = os.path.expanduser("~")
		chooser = Gtk.FileChooserDialog(this_title,action=Gtk.FileChooserAction.OPEN,buttons=( "Cancel", 0, 'Select template', 1))
		chooser.set_default_response(1)
		
		chooser.set_current_folder(homedir+"/Templates")
		response = chooser.run()

#		# process the response
		#print 'Response,', response
		if response == 1:
			# create a template file object and find keywords
			template = TemplateFile(chooser.get_filename())
			
			# getting the extension to specify the mime 
			tpl_ext = os.path.splitext(chooser.get_filename())
			tpl_ext = "*"+tpl_ext[1]

			# create the new text	
			new_text = template.create_text()
			# create a new gedit tab
			new_tab = self.window.create_tab(True)
			doc = new_tab.get_document()
			doc.set_text(new_text)
		else: 
			print('Cancel')
		chooser.destroy()
        
#
## a class
class OpenFileFromTemplate():
	def __init__(self):
		gedit.Plugin.__init__(self)
		self._instances = {}

	def activate(self, window):
		self._instances[window] = OpenFileFromTemplateHelper(self, window)

	def deactivate(self, window):
		self._instances[window].deactivate()
		del self._instances[window]

	def update_ui(self, window):
		self._instances[window].update_ui()
		
#
## a class to hold template file info
class TemplateFile:
	def __init__(self, filename):
		self.filename = filename
		fileobj = open(self.filename)
		self.data = fileobj.read()
		fileobj.close()
		self.keywords = {}
		
	def __del__(self):
		del self.data
		del self.filename
	
	def create_text(self):
		
		return self.data

