import json
import os
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput

# Path for JSON data storage
JSON_FILE = 'inventory_data.json'


class InventoryApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data = self.load_json()  # Load or create the data
        self.current_location = None
        self.current_shelf = None
        self.current_nested_shelf = None
        self.popup_stack = []  # Keep track of open popups

    def build(self):
        # Main layout with the two buttons
        layout = BoxLayout(orientation='vertical', padding=20)

        # Button to go to the location selection page
        go_to_location_button = Button(text="Go To Location", size_hint=(0.5, 0.2))
        go_to_location_button.bind(on_press=self.open_location_page)
        layout.add_widget(go_to_location_button)

        # Button to find an order (search functionality will be added)
        find_order_button = Button(text="Find Order", size_hint=(0.5, 0.2))
        find_order_button.bind(on_press=self.open_find_order_page)
        layout.add_widget(find_order_button)

        return layout

    def open_location_page(self, instance):
        # Popup for selecting or creating a location
        layout = GridLayout(cols=2, padding=10, spacing=10)
        layout.add_widget(Label(text="Select or Create a Location"))

        # Add buttons for existing locations
        for location_name in self.data['locations']:
            button = Button(text=location_name, on_press=lambda btn, location=location_name: self.open_shelves_page(location))
            layout.add_widget(button)

        # Button to create a new location
        create_button = Button(text="Create New Location", on_press=self.create_location_popup)
        layout.add_widget(create_button)

        # Close button
        close_button = Button(text="Close", on_press=self.close_all_popups)
        layout.add_widget(close_button)

        self.popup = Popup(title="Locations", content=layout, size_hint=(0.8, 0.8))
        self.popup_stack.append(self.popup)  # Add to stack
        self.popup.open()

    def open_shelves_page(self, location_name):
        self.current_location = location_name
        layout = GridLayout(cols=2, padding=10, spacing=10)
        layout.add_widget(Label(text=f"Location: {location_name}"))

        # Display buttons for existing shelves
        for shelf_name in self.data['locations'][location_name]['shelves']:
            button = Button(text=shelf_name, on_press=lambda btn, shelf=shelf_name: self.open_nested_shelf_page(shelf))
            layout.add_widget(button)

        # Create new shelf button
        create_shelf_button = Button(text="Create New Shelf", on_press=self.create_shelf_popup)
        layout.add_widget(create_shelf_button)

        # Delete location button
        delete_location_button = Button(text="Delete Location", on_press=self.confirm_location_deletion)
        layout.add_widget(delete_location_button)

        close_button = Button(text="Close", on_press=self.close_all_popups)
        layout.add_widget(close_button)

        self.popup = Popup(title=f"Shelves in {location_name}", content=layout, size_hint=(0.8, 0.8))
        self.popup_stack.append(self.popup)  # Add to stack
        self.popup.open()

    def open_nested_shelf_page(self, shelf_name):
        self.current_shelf = shelf_name
        layout = GridLayout(cols=2, padding=10, spacing=10)
        layout.add_widget(Label(text=f"Shelf: {shelf_name}"))

        # Display buttons for nested shelves
        for nested_shelf_name in self.data['locations'][self.current_location]['shelves'][shelf_name]:
            button = Button(text=nested_shelf_name, on_press=lambda btn, nested_shelf=nested_shelf_name: self.start_scanning(nested_shelf))
            layout.add_widget(button)

        # Create new nested shelf button
        create_nested_shelf_button = Button(text="Create New Nested Shelf", on_press=self.create_nested_shelf_popup)
        layout.add_widget(create_nested_shelf_button)

        # Delete shelf button
        delete_shelf_button = Button(text="Delete Shelf", on_press=self.confirm_shelf_deletion)
        layout.add_widget(delete_shelf_button)

        close_button = Button(text="Close", on_press=self.close_all_popups)
        layout.add_widget(close_button)

        self.popup = Popup(title=f"Nested Shelves in {shelf_name}", content=layout, size_hint=(0.8, 0.8))
        self.popup_stack.append(self.popup)  # Add to stack
        self.popup.open()

    def open_find_order_page(self, instance):
        # Create the layout for finding an order (for now it can be a simple placeholder)
        layout = BoxLayout(orientation='vertical', padding=10)
        layout.add_widget(Label(text="Find Order"))

        # Placeholder TextInput for order search (if needed in the future)
        self.order_search_input = TextInput(hint_text="Enter Order ID", size_hint=(1, 0.2))
        layout.add_widget(self.order_search_input)

        # Button to search for the order
        search_button = Button(text="Search Order", on_press=self.search_order)
        layout.add_widget(search_button)

        # Close button
        close_button = Button(text="Close", on_press=self.close_all_popups)
        layout.add_widget(close_button)

        # Open a popup with this layout
        self.popup = Popup(title="Find Order", content=layout, size_hint=(0.8, 0.8))
        self.popup_stack.append(self.popup)
        self.popup.open()

    def search_order(self, instance):
        # Placeholder function to handle order searching logic
        order_id = self.order_search_input.text.strip()
        if order_id:
            print(f"Searching for order: {order_id}")
        else:
            print("Order ID cannot be empty.")

    def create_location_popup(self, instance):
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(text="Enter new location name:"))
        self.new_location_input = TextInput(hint_text="Location Name", size_hint=(1, 0.2))
        layout.add_widget(self.new_location_input)
        create_button = Button(text="Create", on_press=self.confirm_location_creation)
        layout.add_widget(create_button)
        close_button = Button(text="Close", on_press=self.close_all_popups)
        layout.add_widget(close_button)
        self.popup = Popup(title="New Location", content=layout, size_hint=(0.8, 0.8))
        self.popup_stack.append(self.popup)  # Add to stack
        self.popup.open()

    def confirm_location_creation(self, instance):
        location_name = self.new_location_input.text.strip()
        if location_name and location_name not in self.data['locations']:
            self.data['locations'][location_name] = {"shelves": {}}
            self.save_json()
            print(f"Location '{location_name}' created successfully.")
            self.popup.dismiss()
            self.open_shelves_page(location_name)
        else:
            print("Invalid or duplicate location name.")

    def create_shelf_popup(self, instance):
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(text="Enter new shelf name:"))
        self.new_shelf_input = TextInput(hint_text="Shelf Name", size_hint=(1, 0.2))
        layout.add_widget(self.new_shelf_input)
        create_shelf_button = Button(text="Create Shelf", on_press=self.confirm_shelf_creation)
        layout.add_widget(create_shelf_button)
        close_button = Button(text="Close", on_press=self.close_all_popups)
        layout.add_widget(close_button)
        self.popup = Popup(title="New Shelf", content=layout, size_hint=(0.8, 0.8))
        self.popup_stack.append(self.popup)  # Add to stack
        self.popup.open()

    def confirm_shelf_creation(self, instance):
        shelf_name = self.new_shelf_input.text.strip()
        if shelf_name:
            self.data['locations'][self.current_location]['shelves'][shelf_name] = {}
            self.save_json()
            print(f"Shelf '{shelf_name}' created successfully.")
            self.popup.dismiss()
            self.open_nested_shelf_page(shelf_name)
        else:
            print("Invalid shelf name.")

    def create_nested_shelf_popup(self, instance):
        # Auto-generate next available nested shelf name
        nested_shelf_name = self.get_next_nested_shelf_name()
        self.data['locations'][self.current_location]['shelves'][self.current_shelf][nested_shelf_name] = {}
        self.save_json()
        print(f"Nested Shelf '{nested_shelf_name}' created successfully.")
        self.popup.dismiss()
        self.open_nested_shelf_page(self.current_shelf)

    def get_next_nested_shelf_name(self):
        """Find the next available nested shelf name (e.g., A1, A2, etc.)."""
        nested_shelves = self.data['locations'][self.current_location]['shelves'][self.current_shelf]
        existing_names = [name for name in nested_shelves]
        i = 1
        while f"{self.current_shelf}{i}" in existing_names:
            i += 1
        return f"{self.current_shelf}{i}"

    def start_scanning(self, nested_shelf_name):
        self.current_nested_shelf = nested_shelf_name
        print(f"Now scanning items on shelf {nested_shelf_name}")

    def confirm_location_deletion(self, instance):
        layout = BoxLayout(orientation='vertical', padding=10)
        layout.add_widget(Label(text="Are you sure you want to delete this location and all its contents?"))
        yes_button = Button(text="Yes", on_press=self.delete_location)
        no_button = Button(text="No", on_press=self.close_all_popups)
        layout.add_widget(yes_button)
        layout.add_widget(no_button)
        self.popup = Popup(title="Delete Location", content=layout, size_hint=(0.6, 0.4))
        self.popup_stack.append(self.popup)  # Add to stack
        self.popup.open()

    def delete_location(self, instance):
        del self.data['locations'][self.current_location]
        self.save_json()
        print(f"Location '{self.current_location}' deleted successfully.")
        self.popup.dismiss()
        self.open_location_page(None)

    def confirm_shelf_deletion(self, instance):
        layout = BoxLayout(orientation='vertical', padding=10)
        layout.add_widget(Label(text="Are you sure you want to delete this shelf and all its contents?"))
        yes_button = Button(text="Yes", on_press=self.delete_shelf)
        no_button = Button(text="No", on_press=self.close_all_popups)
        layout.add_widget(yes_button)
        layout.add_widget(no_button)
        self.popup = Popup(title="Delete Shelf", content=layout, size_hint=(0.6, 0.4))
        self.popup_stack.append(self.popup)  # Add to stack
        self.popup.open()

    def delete_shelf(self, instance):
        del self.data['locations'][self.current_location]['shelves'][self.current_shelf]
        self.save_json()
        print(f"Shelf '{self.current_shelf}' deleted successfully.")
        self.popup.dismiss()
        self.open_shelves_page(self.current_location)

    def save_json(self):
        with open(JSON_FILE, 'w') as f:
            json.dump(self.data, f, indent=4)

    def load_json(self):
        if os.path.exists(JSON_FILE):
            with open(JSON_FILE, 'r') as f:
                return json.load(f)
        else:
            return {"locations": {}}

    def close_all_popups(self, instance=None):
        # Close all popups
        for popup in self.popup_stack:
            popup.dismiss()
        self.popup_stack.clear()


if __name__ == '__main__':
    InventoryApp().run()

