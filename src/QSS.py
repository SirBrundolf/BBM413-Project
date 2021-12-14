qss = """
QPushButton
{
    font-family: 'Montserrat', Arial;
    font-size: 30px;
    color: #f0f0f0;
    background-color: #282828;
    border: 4px solid #0078d7;
    border-radius: 25px;
}
QPushButton::hover
{
    background-color: #0078d7;
    border: transparent;
}
QSpinBox, QDoubleSpinBox
{
    font-family: 'Montserrat', Arial;
    font-size: 20px;
    color: #f0f0f0;
    background-color: #535353;
    border: 4px #f0f0f0;
}
QCheckBox
{
    font-family: 'Montserrat', Arial;
    font-size: 20px;
    color: #f0f0f0;
}
QLabel[accessibleName='text_field']
{
    font-family: 'Montserrat', Arial;
    font-size: 20px;
    color: #f0f0f0;
}
QLabel[accessibleName='about_text_field']
{
    font-family: 'Montserrat', Arial;
    font-size: 60px;
    color: #f0f0f0;
}
QLabel[accessibleName='start_text']
{
    font-family: 'Montserrat', Arial;
    font-size: 60px;
    color: #f0f0f0;
    border: 6px dashed #f0f0f0;
}
QLabel[accessibleName='loaded_image_frame'], QLabel[accessibleName='manipulated_image_frame']
{
    background: transparent;
}
QMainWindow, NewWindow, AboutWindow
{
    background-color: #282828;
}
QMenuBar
{
    padding: 3px 0px;
    background-color: #535353;
}
QMenuBar::item
{
    padding: 2px 10px;
    margin: 0px 0px 0px 5px;
    color: #f0f0f0;
}
QMenuBar::item:selected
{
    background-color: #474747;
    border: 2px solid #656565;
    border-radius: 5px;
}
QMenuBar::item:pressed
{
    background: #383838;
}

QMenu
{
    background-color: #f0f0f0;
    margin: 2px;
}
QMenu::item
{
    background-color: transparent;
}
QMenu::item:selected
{
    color: #ffffff;
    background-color: #0078d7;
}
"""
