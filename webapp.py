import flet as ft

from utils import CMDLineArguments, DetectionsParser, EnvLoader









async def main(page: ft.Page):

    p = CMDLineArguments()
    env = EnvLoader()
    login, passw = env.get_stk().values()
    print(login,passw)
    d = DetectionsParser(login,passw)
    options = p.parse_args()
    t = await d.get_token()
    all_d = await d.get_all_detections(t)
    if not all_d: all_d = 1337
    page.title = "leet"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    txt_number = ft.Text(all_d)


    page.add(
        ft.Row(
            [txt_number],
            alignment=ft.MainAxisAlignment.CENTER,
        )
    )

ft.app(main)