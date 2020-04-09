"""
Very simple pygame GUI solution
"""
import pygame


class Menu:
    """
    Creates a Menu that contains various widgets\n
     - screen: pygame display
     - theme: Theme that is defaulty used for all widgets
     - Menu.update() needs to be called every frame 
     - Color: sets color, can also have alpha (r,g,b,a)
     - x, y, width, height: modify the size of the menu(doesn'y modifi the size of widgets inside the menu)
    """
    def __init__(self, screen, theme=None, color_bg=(150,150,150), x=0, y=0, width=None, height=None):
        self.screen = screen
        self.theme = Theme() if theme is None else theme
        self.color_bg = color_bg
        self.widgets = []
        self.clock = pygame.time.Clock()
        self.x = x
        self.y = y
        self.width = screen.get_size()[0] if width is None else width
        self.height = screen.get_size()[1] if height is None else height

        self.fill_surface = pygame.Surface((self.width, self.height))
        if len(self.color_bg) == 4:
            self.fill_surface.fill(self.color_bg[:3]) 
            self.fill_surface.set_alpha(self.color_bg[3])
        else:
            self.fill_surface.fill(self.color_bg[:3])

    def update(self):
        """
        Updates all the widgets.
        """
        #Handle events and responses
        events = pygame.event.get()
        result = "self"
        for event in events:
            if event.type == pygame.QUIT:
                return "quit"
        for widget in self.widgets:
            result_ = widget.update(events)
            if result_ != "self":
                result = result_
        #Draw stuff
        self.screen.blit(self.fill_surface, (self.x, self.y))
        for widget in self.widgets:
            draw_func = getattr(widget, "draw", None)
            if draw_func is not None:
                widget.draw()
        pygame.display.update()
        return result
            
    def _assign_widget(self, widget):
        """
        Function used by other widgets to assign themeself to this Menu.
        Tou don't need to worry about this function
        """
        self.widgets.append(widget)

    def remove_widget(self, widget):
        self.widgets.remove(widget)

class GenericWidget:
    """
    Preset for a widget. If not specified otherwise all widgets share the options of this class, but not every option might be used
     - text: specifies the text that is displayed by the widget
    All of the text style args override the default theme text values. If you want to change these values dynamicly use set_text(), set_text_styles()
     (added here for a more conveniet way of changing them and not having to make another theme)
    """
    def __init__(self, parent, x, y, width, height, theme=None, 
                text="text", text_size=None, text_font_name=None, text_color=None, text_bold=None, text_italic=None, text_color_disabled=None):
        self.parent = parent
        if isinstance(parent, pygame.Surface):
            self.screen = parent
        else:
            self.screen = parent.screen
            theme = parent.theme if theme is None else theme
            parent._assign_widget(self)
        self.state = "normal" #can be normal, hover, pressed or (disabled(this needs to be added))
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.theme = Theme() if theme is None else theme
        #Handle text variables
        self.text_size = self.theme.text_size if text_size is None else text_size
        self.text_font_name = self.theme.text_font_name if text_font_name is None else text_font_name
        self.text_color = self.theme.text_color if text_color is None else text_color
        self.text_color_disabled = self.theme.text_color_disabled if text_color_disabled is None else text_color_disabled
        self.text_bold = self.theme.text_bold if text_bold is None else text_bold
        self.text_italic = self.theme.text_italic if text_italic is None else text_italic
        self.text_font = pygame.font.SysFont(self.text_font_name, self.text_size, self.text_bold, self.text_italic)
        self.set_text(text)

    def set_text_style(self, text_size=None, text_font_name=None, text_color=None, text_bold=None, text_italic=None):
        """
        Use this function if you want to set text style. Do NOT directly modify the values of text style variables.
        """
        self.text_size = self.text_size if text_size is None else text_size
        self.text_font_name = self.text_font_name if text_font_name is None else text_font_name
        self.text_color = self.text_color if text_color is None else text_color
        self.text_color_disabled = self.theme.text_color_disabled if text_color_disabled is None else text_color_disabled
        self.text_bold = self.text_bold if text_bold is None else text_bold
        self.text_italic = self.text_italic if text_italic is None else text_italic
        self.text_font = pygame.font.SysFont(self.text_font_name, self.text_size, self.text_bold, self.text_italic)
        self.text_rendered = self.text_font.render(self.text, True, self.text_color)

    def set_text_style_deffault(self):
        """
        Sets the text style to the one in the theme.
        """
        self.text_size = self.theme.text_size
        self.text_font_name = self.theme.text_font
        self.text_color = self.theme.text_color
        self.text_color_disabled = self.theme.text_color_disabled
        self.text_bold = self.theme.text_bold
        self.text_italic = self.theme.text_italic
        self.text_font = pygame.font.SysFont(self.text_font_name, self.text_size, self.text_bold, self.text_italic)
        self.text_rendered = self.text_font.render(self.text, True, self.text_color)

    def set_text(self, text):
        self.text = text
        text_color = self.text_color
        if self.state == "disabled":
            text_color = self.text_color_disabled
        self.text_rendered = self.text_font.render(self.text, True, self.text_color)
        self.text_width, self.text_height = self.text_font.size(self.text)

    def draw(self):
        self.color = self.theme.color_normal
        if self.state == "hover":
            self.color = self.theme.color_hover
        elif self.state == "pressed":
            self.color = self.theme.color_clicked
        elif self.state == "disabled":
            self.color = self.theme.color_disabled

    def update(self, events=None):
        return "self"


class Theme:
    """
    Container with all the infor about colors and dizajn of 'widgets'
    Mainly used so you can mantain an uniform style across multiple widgets
    text_size is in characters
    """
    def __init__(self, color_normal=(30, 30, 30), color_hover=(50, 50, 50), color_clicked=(100, 100, 100), color_disabled=(20, 20, 20),
                 text_size=20, text_font_name="Verdana", text_color=(200, 200, 200), text_bold=False, text_italic=False, text_color_disabled=(100, 100, 100)):
        self.color_normal = color_normal
        self.color_hover = color_hover
        self.color_clicked = color_clicked
        self.color_disabled = color_disabled
        self.text_color = text_color
        self.text_size = text_size
        self.text_font_name = text_font_name
        self.text_bold = text_bold
        self.text_italic = text_italic
        self.text_color_disabled = text_color_disabled
        #self.text_font = pygame.font.SysFont(self.text_font_name, self.text_size, self.text_bold, self.text_italic) TODO mby remove


class Button(GenericWidget):
    """
    You click this something happens.\n
     - parent can be set to a Menu object if you want this under a Menu otherwise used to define pygame screen
     - command can be either a function that will be called, or a string that will be returned in update method
     - for theme create a Theme object
     - contionus: if the command should trigger on MOUSEBUTTONDOWN(True) or on MOUSEBUTTONUP(False)
    You can also pass here any keyword argumnet that is used by GenericWidget
    """
    #ADD ANCHOR
    def __init__(self, parent, x, y, width, height, command, theme=None, continous=False, **kw):
        super().__init__(parent, x, y, width, height, theme, **kw)
        self.command = command
        self.continous = continous

    def draw(self):
        super().draw()
        pygame.draw.rect(self.screen, self.color, (self.x, self.y, self.width, self.height))
        text_width, text_height = self.text_font.size(self.text)
        cords = (self.x + self.width//2 - text_width//2, self.y + self.height//2 - text_height//2, text_width, text_height)
        self.screen.blit(self.text_rendered, cords)

    def update(self, events=None):
        if self.state == "disabled":
            return "self"
        events = pygame.event.get() if events is None else events
        result = "self"
        for event in events:
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.MOUSEMOTION:
                mouse_pos = pygame.mouse.get_pos()
                if self.x < mouse_pos[0] < self.x + self.width and self.y < mouse_pos[1] < self.y + self.height:
                    self.state = "hover"
                elif self.state == "hover":
                    self.state = "normal"
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if self.x < mouse_pos[0] < self.x + self.width and self.y < mouse_pos[1] < self.y + self.height:
                    self.state = "pressed"
                    if self.continous:
                        if isinstance(self.command, str):
                            result = self.command
                        else:
                            self.command()
                elif self.state == "pressed":
                    self.state = "normal"
            if event.type == pygame.MOUSEBUTTONUP:
                mouse_pos = pygame.mouse.get_pos()
                if self.x < mouse_pos[0] < self.x + self.width and self.y < mouse_pos[1] < self.y + self.height:
                    if self.continous is False:
                        if isinstance(self.command, str):
                            result = self.command
                        else:
                            self.command()
                    if self.state == "pressed":
                        self.state = "hover"
                elif self.state == "pressed":
                    self.state = "normal"
        return result


class Label(GenericWidget):
    """
    Used to display text
     - text_allign: how to allign text around x,y. Centre(C), North (N), South East (SE)...
     - to change text use Label().change_text()
    You can also pass here any keyword argumnet that is used by GenericWidget
    """
    def __init__(self, parent, x, y, text, theme=None, text_anchor="C", **kw):
        self.text_anchor = text_anchor
        super().__init__(parent, x, y, 0, 0, theme, text=text, **kw)
        self._anchor()

    def set_text(self, text, anchor=True):
        """
        Changes text\n
         - anchor: if text is supoused to be again alligned to anchor
        """
        super().set_text(text)
        if anchor:
            self._anchor()

    def _anchor(self):
        """
        Allgins the text to text_anchor needs to be called each time the size, font, etc. is changed.
        """
        self.width, self.height = self.text_font.size(self.text)
        self.cords = [self.x - self.width//2, self.y - self.height//2, self.width, self.height]
        if self.text_anchor == "C":
            return
        if "N" in self.text_anchor:
            self.cords[1] += self.height//2
        if "S" in self.text_anchor:
            self.cords[1] -= self.height//2
        if "W" in self.text_anchor:
            self.cords[0] += self.width//2
        if "E" in self.text_anchor:
            self.cords[0] -= self.width//2

    def draw(self):
        self.screen.blit(self.text_rendered, self.cords)


class KeyBind(GenericWidget):
    """
    Widget used to set keybindings. When user clicks the widget it will record the next key that is pressed  
    (doesn't work for mouse click bind)\n
    You can also pass here any keyword argumnet that is used by GenericWidget
    """
    def __init__(self, parent, x, y, width, height, theme=None, def_key=None, **kw):
        super().__init__(parent, x, y, width, height, theme, **kw)
        self.key = def_key
        self.set_text("None" if def_key is None else pygame.key.name(def_key))
    
    def update(self, events=None):
        if self.state == "disabled":
            return "self"
        events = pygame.event.get() if events is None else events
        result = "self"
        for event in events:
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.MOUSEMOTION:
                mouse_pos = pygame.mouse.get_pos()
                if self.x < mouse_pos[0] < self.x + self.width and self.y < mouse_pos[1] < self.y + self.height and self.state != "pressed":
                    self.state = "hover"
                elif self.state == "hover":
                    self.state = "normal"
            if event.type == pygame.MOUSEBUTTONUP:
                mouse_pos = pygame.mouse.get_pos()
                if self.x < mouse_pos[0] < self.x + self.width and self.y < mouse_pos[1] < self.y + self.height:
                    self.state = "pressed"
                else:
                    self.state = "normal"
            if event.type == pygame.KEYUP and self.state == "pressed":
                self.key = event.key
                self.set_text(pygame.key.name(self.key))
                self.state = "normal"
        return result

    def draw(self):
        super().draw()
        color = self.theme.color_normal
        if self.state == "hover":
            color = self.theme.color_hover
        elif self.state == "pressed":
            color = self.theme.color_clicked
        pygame.draw.rect(self.screen, self.color, (self.x, self.y, self.width, self.height))
        cords = (self.x + self.width//2 - self.text_width//2, self.y + self.height//2 - self.text_height//2, self.text_width, self.text_height)
        self.screen.blit(self.text_rendered, cords)

class Rectangle(GenericWidget):
    """
    Just a rectangle
    """
    def __init__(self, parent, x, y, width, height, color):
        super().__init__(parent, x, y, width, height)
        self.color = color
    
    def draw(self):
        pygame.draw.rect(self.screen, self.color, (self.x, self.y, self.width, self.height))


if __name__ == "__main__":
    pygame.init()
    pygame.font.init()
    test_screen = pygame.display.set_mode((500,500))
    done = False
    test = Menu(test_screen)
    btn = Button(test, 50, 150, 100, 50, lambda: print("Test"), text="click")
    label = Label(test, 250, 75, "Test Menu", text_size=75)
    kybd = KeyBind(test, 200, 150, 100, 25)
    while not done:
        result_ = test.update()
        #pygame.display.update()
        if result_ == 'quit':
            done = True
    pygame.quit()