from prompt_toolkit.key_binding.bindings.focus import focus_next, focus_previous
from prompt_toolkit.document import Document
from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import Float, FloatContainer, Window, HSplit, WindowAlign
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.layout import FloatContainer, Float
from prompt_toolkit.widgets import Dialog, Label, Button
from prompt_toolkit.widgets import Frame, TextArea
import rules as rl
import os
from PIL import Image

# 1. The layout
output_field_p = TextArea(focusable=False)
input_field_p = TextArea(
        height=1,
        prompt="Premises >>> ",
        multiline=False,
        wrap_lines=False,
    )
input_field_c = TextArea(
        height=1,
        prompt="Conclusion >>> ",
        multiline=False,
        wrap_lines=False,
    )

conclusion = HSplit(
            [
                # output_field,
                # Window(FormattedTextControl("Conclusion"),height=2,align=WindowAlign.CENTER),
                input_field_c,
                ],
            style='bg:#2f4f4f'
            )
premisas = HSplit(
            [
                # output_field,
                Window(FormattedTextControl("Premises"),height=2,align=WindowAlign.CENTER),
                output_field_p,
                Window(height=1, char="-", style="class:line"),
                input_field_p,
                ],
            style='bg:#2f4f4f'
            )


body = FloatContainer(
    content=Window(FormattedTextControl(""), wrap_lines=True),
    floats=[
        Float(
            HSplit([
                Frame(premisas),
                Frame(conclusion),
                ]),
            height=20,
            width=50
        ),
    ],
)


# 2. Key bindings
kb = KeyBindings()
kb = KeyBindings()
kb.add("tab")(focus_next)
kb.add("s-tab")(focus_previous)
@kb.add("c-c")
def _(event):
    "Quit application."
    event.app.exit()


# 3. The `Application`
application = Application(layout=Layout(body), key_bindings=kb, full_screen=True)

    
def create_dialog_simple(title,text):
    return  Dialog(
                title=title,
                body=Label(text=text, dont_extend_height=True))

# 4. Functions
def accept_p(buff):
    output = input_field_p.text.replace(" ","")
    new_text = output_field_p.text +"\n"+ output
    output_field_p.buffer.document = Document(
        text=new_text, cursor_position=len(new_text)
    )

def accept_c(buff):
    output = input_field_c.text
    premises = output_field_p.text.split()
    result =rl.test_theorem(output,premises)
    os.system('notify-send "'+str(result)+'"')
    im1 = Image.open(r"/home/karu/test.png") 
    im1.show()
    if result:
        im2 = Image.open(r"/home/karu/model.png") 
        im2.show()

input_field_p.accept_handler = accept_p
input_field_c.accept_handler = accept_c

def run():
    application.run()


if __name__ == "__main__":
    run() 
