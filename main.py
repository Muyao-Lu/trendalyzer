import os
# os.environ["KIVY_NO_CONSOLELOG"] = "True"
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Rectangle, Color, Line, SmoothLine
from kivy.clock import Clock
import web as w
import datetime
from data import *

Window.minimum_width = 600
Window.minimum_height = 600
queries = []
start_date = None
end_date = None

add_query_input = None
add_query_button = None
query_box = None
warning_widget = None
start_date_input = None
end_date_input = None

search_data = {"region": "", "stype": "", "scat": ""}

def check_date_type_validity(date: dict) -> bool:
    year = date["year"]
    month = date["month"]
    day = date["day"]
    today = datetime.date.today()
    if year is None or month is None or day is None:
        return False
    if int(year) <= 0 or int(month) <= 0 or int(day) <= 0:
        return False
    if int(year) > today.year or int(year) < 2004:
        return False
    elif int(year) == today.year:
        if int(month) > today.month:
            return False
        elif int(month) == today.month:
            if int(day) > today.day:
                return False
    if not check_month_validity(year, month, day):
        return False

    return True

def check_date_time_validity(date_before: dict, date_after: dict) -> bool:
    if date_before["year"] > date_after["year"]:
        return False
    elif date_before["year"] == date_after["year"]:
        if date_before["month"] > date_after["month"]:
            return False
        elif date_before["month"] == date_after["month"]:
            if date_before["day"] >= date_after["day"]:
                return False

    return True


def process_date(date: str, sep: str) -> dict:
    write_to = "year"
    year = ""
    month = ""
    day = ""
    for char in date:
        if char != sep:
            if write_to == "year":
                year += char
            elif write_to == "month":
                month += char
            elif write_to == "day":
                day += char
        else:
            if write_to == "year":
                write_to = "month"
            elif write_to == "month":
                write_to = "day"
    return {"year": int(year), "month": int(month), "day": int(day)}


def check_month_validity(year: int, month: int, date_to_check: int) -> bool:
    months_dict = {1: 31, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}
    if month == 2:
        if not year % 100 == 0:
            if year % 4 == 0 or year % 400 == 0:
                if date_to_check <= 29: return True
                else: return False
            else:
                if date_to_check <= 28: return True
                else: return False
        else:
            if date_to_check <= 28: return True
            else: return False
    else:
        if date_to_check <= months_dict[month]: return True
        else: return False


class QueryBoxLayout(BoxLayout):

    def __init__(self, **kwargs):
        global query_box
        super().__init__(**kwargs)
        self.size_hint = 1, None
        self.orientation = "vertical"
        self.font_family = "textures\\DMsans.ttf"
        self.update_queries()
        query_box = self

    def update_queries(self):
        for i in range(len(self.children)):
            self.remove_widget(self.children[0])
        for query in queries:
            query_text = Button(text=query, color="#7d807d", height=10, background_normal="", on_press=lambda x: self.remove_item(query))
            self.add_widget(query_text)
            self.height += 10

    def remove_item(self, query):
        global queries
        queries.remove(query)
        self.update_queries()
        warning_widget.activate_warning("\"{query}\" successfully removed".format(query=query), "#008b00", critical=False)



class AddQueryButton(Button):

    def __init__(self, **kwargs):
        global add_query_button
        super().__init__(**kwargs)
        self.size_hint = 1, 0.2
        self.background_normal = ""
        self.background_color = "#a9aaa9"
        self.color = "#f6f8fc"
        self.text = "+"
        self.on_press = self.add_queries
        self.popup = None
        add_query_button = self

    def add_queries(self):
        container = BoxLayout(orientation="vertical")
        container.add_widget(AddQueryInput())
        container.add_widget(Widget(size_hint=(1, 0.25)))
        container.add_widget(SubmitButton())
        self.popup = Popup(title="Add Search Query",
                      content=container,
                      size_hint=(0.8, 0.3),
                      separator_height=0,
                      title_font="textures\\DMsans.ttf",
                      title_align="center",
                      title_size=min(Window.width*0.6/16, Window.height*0.6),
                      background="",
                      background_color="#a9aaa9",
                      title_color="#7d807d")
        self.popup.open()

    def dismiss(self):
        self.popup.dismiss()


class AddQueryInput(TextInput):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        global add_query_input
        self.multiline = False
        self.halign = "center"
        self.cursor_color = 0, 0, 0, 0
        self.foreground_color = "#7d807d"
        self.size_hint = 1, 0.5
        self.hint_text = "Query to search."

        add_query_input = self


class SubmitButton(Button):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.text = "Submit"
        self.background_normal = ""
        self.background_color = "#f6f8fc"
        self.color = "#7d807d"
        self.size_hint = 1, 0.5

    def on_press(self):
        if add_query_input.text.replace(" ", "").lower() != "":
            queries.append(add_query_input.text.lower())
        else:
            warning_widget.activate_warning("Can't add a blank query!", "#8b0000")

        add_query_button.dismiss()
        query_box.update_queries()


class SettingText(Label):
    def __init__(self, coefficients, **kwargs):
        super().__init__(**kwargs)
        self.coefficients = coefficients
        self.font_size = min(self.width * coefficients["width"], self.height * coefficients["height"])
        self.text_size = self.size
        self.text_size = self.size
        self.halign = "center" # change to left later
        self.valign = "center"

    def on_size(self, *args):
        self.font_size = min(self.width * self.coefficients["width"], self.height * self.coefficients["height"])
        self.text_size = self.size

class SettingInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.width = min(Window.width * 0.4 * 0.9, Window.height / 20 * 7.5)
        self.height = min(self.width / 7.5, Window.height / 20 * 0.9)
        self.pos_hint = {"center_y": 0.5, "center_x": 0.5}
        self.text_size = self.size
        self.foreground_color = "#7d807d"
        # hint_text_color: "#a9aaa9"
        self.background_color = (246 / 255, 248 / 255, 252 / 255, 0)
        self.cursor_color = 0, 0, 0, 0
        self.multiline = False
        self.font_size = self.height / 2
        self.halign = "center"
        self.valign = "center"
        self.font_name = "textures\\DMsans.ttf"
        self.curve = 50
        self.past_size = (None, None)

    def on_size(self, *args):
        try:
            if self.size != self.past_size:
                self.width = min(Window.width * 0.4 * 0.9, Window.height / 20 * 7.5)
                self.height = min(self.width / 7.5, Window.height / 20 * 0.9)
                self.curve = 50
                self.canvas.after.clear()
                self.text_size = self.size
                self.font_size = self.height / 2

                with self.canvas.after:
                    Color(rgb=(125 / 255, 128 / 255, 125 / 255))

                    Line(points=(self.x + self.curve/2, self.y, self.x + self.width - self.curve/2, self.y),
                         width=1.5)

                    Line(points=(self.x + self.curve/2, self.y + self.height, self.x + self.width - self.curve/2, self.y + self.height),
                         width=1.5)

                    SmoothLine(width=1.75,
                               ellipse=(self.x, self.y, self.curve, self.height, 0, -180, 100))

                    SmoothLine(width=1.75,
                               ellipse=(self.x + self.width - self.curve, self.y, self.curve, self.height, 0, 180, 100))
            self.past_size = args[1]
        except AttributeError:
            pass
class HeaderButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # grid = GridLayout(size_hint=(1, 0.8),
        #                   pos_hint={"top": 1},
        #                   cols=2,
        #                   spacing=min(Window.width, Window.height)/50,
        #                   padding=min(Window.width, Window.height)/50)
        # grid.add_widget(SettingText(coefficients={"width": 1/12, "height": 0.45},
        #                             text="Download Location: ",
        #                             color="#7d807d"))
        # grid.add_widget(SettingInput())
        # grid.add_widget(
        #     SettingText(coefficients={"width": 1/24, "height": 0.2},
        #                 text="Location to download results to. Defaults to directory where this program is located",
        #                 color="#7d807d"))
        # grid.add_widget(Widget())
#
        # grid.add_widget(SettingText(coefficients={"width": 1/12, "height": 0.45},
        #                             text="Download Name: ",
        #                             color="#7d807d"))
        # grid.add_widget(SettingInput())
#
        # grid.add_widget(
        #     SettingText(coefficients={"width": 1/24, "height": 0.2},
        #                 text="Name to give file containing results. Defaults to results.xlsx",
        #                 color="#7d807d", ))
        # grid.add_widget(Widget())
#
        # grid.add_widget(SettingText(coefficients={"width": 1/12, "height": 0.45},
        #                             text="Create popularity graph: ",
        #                             color="#7d807d"))
        # grid.add_widget(ToggleButton())
#
        # grid.add_widget(
        #     SettingText(coefficients={"width": 1/24, "height": 0.2},
        #                 text="Toggle to create/disable the creation of a MatPlotLib graph with results. Defaults to False",
        #                 color="#7d807d", ))
        # grid.add_widget(Widget())

        self.popup = Popup(title="Settings",
                           content=SettingText(coefficients={"width": 1/24, "height": 0.2},
                                               text="Coming Soon!",
                                               halign="center",
                                               color="#7d807d",
                                               pos_hint={"center_x": 0.5}),
                           size_hint=(0.8, 0.8),
                           separator_height=5,
                           title_font="textures\\DMsans.ttf",
                           title_align="center",
                           title_size=min(Window.width * 0.6 / 16, Window.height * 0.6),
                           background="",
                           background_color="#a9aaa9",
                           title_color="#7d807d",
                           separator_color="#7d807d")

    def on_press(self, *args):
        self.popup.open()


class SubmitDropdownButton(Button):
    button_type = ObjectProperty("")
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dropdown = SubmitDropdown(max_height=Window.height/5)
        Clock.schedule_once(self.post_init, 0.01)

    def post_init(self, *args):
        for i in range(len(dropdown_data[self.button_type])):
            if type(dropdown_data[self.button_type]) == list:
                self.dropdown.add_widget(SubmitDropdownElementButton(dropdown_data[self.button_type][i], self.button_type, self))
            else:
                temp_id = list(dropdown_data[self.button_type].keys())[i]
                self.dropdown.add_widget(SubmitDropdownElementButton(temp_id, self.button_type, self, dropdown_data[self.button_type][temp_id]))
    def update_text_size(self):
        if len(self.text) > 20:
            self.font_size = self.width/(len(self.text)/2)

    def on_size(self, *args):
        if len(self.text) > 20:
            self.font_size = self.width/(len(self.text)/2)
        else:
            self.font_size = self.height / 2

    def open_dropdown(self):
        self.dropdown.open(self)


class SubmitDropdown(DropDown):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class SubmitDropdownElementButton(Button):

    def __init__(self, id: str, type: str, parent: Widget, alt_data=None, **kwargs):
        super().__init__(**kwargs)
        self.type = type
        self.id = id
        self.text = id
        self.alt = alt_data
        self.parent_widget = parent
        self.height = Window.height / 30
        self.size_hint_y = None
        self.background_normal = ""
        self.background_color = "#7d807d"
        self.color = "#a9aaa9"
        self.font_size = min(self.width/(len(self.text)/4), self.height/1.5)

    def on_press(self, *args):
        global search_data
        self.parent_widget.text = self.id
        self.parent_widget.update_text_size()

        if self.alt is None:
            search_data[self.type] = self.id
        else:
            search_data[self.type] = self.alt

class SubmitInput(TextInput):
    input_type = ObjectProperty("")
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.post_init, 0.01)

    def post_init(self, *args):
        global start_date_input, end_date_input
        if self.input_type == "from":
            start_date_input = self
        else:
            end_date_input = self

    def insert_text(self, substring, from_undo=False):
        if substring.isdigit() or substring == "/":

            return super().insert_text(substring, from_undo=from_undo)
        else:
            pass

    def update_var(self):
        global start_date, end_date
        if self.input_type == "from":
            start_date = self.text.replace("/", "-")
        else:
            end_date = self.text.replace("/", "-")

class DynamicText(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class RunButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def run_scraper(self):
        if len(queries) > 0:
            start_date_input.update_var()
            end_date_input.update_var()
            if start_date is not None and end_date is not None:
                try:
                    start_data = process_date(start_date, "-")
                    end_data = process_date(end_date, "-")
                except ValueError:
                    warning_widget.activate_warning("Invalid dates! Not enough data!", "#8b0000")
                    return
                if check_date_type_validity(start_data) and check_date_type_validity(end_data):
                    if check_date_time_validity(start_data, end_data):
                        start_date_processed = str(start_data["year"]) + "-" + str(start_data["month"]) + "-" + str(start_data["day"])
                        end_date_processed = str(end_data["year"]) + "-" + str(end_data["month"]) + "-" + str(end_data["day"])

                        w.setup(queries, start_date=start_date_processed, end_date=end_date_processed, search_data=search_data)
                    else:
                        warning_widget.activate_warning("Can't do search when start date is after end date!", "#8b0000")
                        return
                else:
                    warning_widget.activate_warning("Invalid dates! Can't do a search in the future, before 2004, or on nonexistent dates!", "#8b0000")
                    return
            else:
                warning_widget.activate_warning("Incomplete data! Fill in both date fields!", "#8b0000")
                return
        else:
            warning_widget.activate_warning("Can't do search with a empty search query!", "#8b0000")
            return

        container = BoxLayout(orientation="vertical")
        container.add_widget(scroll := ScrollView())
        scroll.add_widget(DynamicText(text="While search is occurring please do not: "+
                                        "\n \u2022   Exit any tabs opened by program "+
                                        "\n \u2022   Move mouse "+
                                        "\n \u2022   Switch to a new tab"+
                                        "\n \u2022   Open any new applications"+
                                        "\n \u2022   [b]Except to fill out any reCAPTCHA(s) due to suspicious activity. "+
                                        "\n(Google trends will give these if they detect you spamming their system)[/b] "+
                                        "\nwhile the program is running. Once you click confirm, this window will freeze and resume "+
                                        "once search is done. To interrupt search, press [b]CTRL+C[/b]",
                                        size_hint=(1, None),
                                        color="#7d807d",
                                        height=Window.height/2,
                                        font_size = min(Window.width/35, Window.height/35),
                                        halign="left",
                                        valign="top",
                                        markup=True))
        container.add_widget(Button(text="Yes, I have diligently read all of the above text and am ready to begin",
                                    size_hint=(1, 0.2),
                                    background_normal = "",
                                    background_color = "#f6f8fc",
                                    color = "#7d807d",
                                    on_press=self.do_search
                                    ))
        self.popup = Popup(title="Are you sure you want to begin search",
                           content=container,
                           size_hint=(0.8, 0.6),
                           separator_height=5,
                           title_font="textures\\DMsans.ttf",
                           title_align="center",
                           title_size=min(Window.width * 0.6 / 16, Window.height * 0.6),
                           background="",
                           background_color="#a9aaa9",
                           title_color="#7d807d",
                           separator_color="#7d807d")
        self.popup.open()

    def do_search(self, *args):
        self.popup.dismiss()
        try:
            save_location = w.main()
            warning_widget.activate_warning("Search complete! Results saved at {sl} (Click to dismiss)".format(sl=save_location), "#008b00", critical=True)
        except IndexError:
            warning_widget.activate_warning("Not enough search data! Expand timeframe or chose a different country/category! (Click to dismiss)", "#8b0000", critical=True)
        except RuntimeError:
            warning_widget.activate_warning("Something went wrong. Check your internet connection! (Click to dismiss)", "#8b0000", critical=True)
        except PermissionError:
            warning_widget.activate_warning("Permission denied. Close all open files and try again", "#8b0000", critical=True)

class WarningWidget(Button):

    def __init__(self, **kwargs):
        global warning_widget
        super().__init__(**kwargs)
        self.pos = 0, 0
        self.size_hint = (0.5, 0.05)
        self.active = False
        self.warning_critical = False
        self.opacity = 0
        self.valign = "center"
        self.halign = "left"
        self.font_name = "textures\\DMsans.ttf"
        self.background_normal = ""
        warning_widget = self

    def activate_warning(self, warning_text, color, critical=False):
        self.active = True
        self.warning_critical = critical
        self.opacity = 1
        self.text = warning_text
        self.background_color = color
        self.font_size = min(self.height, self.width) / 3
        self.text_size = self.size
        self.padding = min(Window.width, Window.height) / 100
        if not self.warning_critical:
            Clock.schedule_once(lambda x: Clock.schedule_interval(self.fade_out, 0.01), 2)
        else:
            pass

    def on_size(self, *args):
        self.font_size = min(self.height, self.width) / 3
        self.padding = min(Window.width, Window.height) / 100
        self.text_size = self.size

    def fade_out(self, *args):
        if self.opacity >= 0:
            self.opacity -= 0.01
        else:
            self.opacity = 0
            Clock.unschedule(self.fade_out)

    def on_press(self):
        if self.warning_critical:
            self.active = False
            self.opacity = 0


class MainApp(App):
    icon = "textures\\icon.png"
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

def main():
    MainApp().run()


if __name__ == "__main__":
    main()


