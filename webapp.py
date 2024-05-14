import asyncio
import flet as ft

from utils import CMDLineArguments, DetectionsParser, EnvLoader


async def main(page: ft.Page):

    env = EnvLoader()
    login, passw = env.get_stk().values()

    d = DetectionsParser(login, passw)
    t:str = await d.get_token()
    try:
        all_d = await d.get_all_detections(t)
    except Exception('Empty response'):
        all_d = 1337

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
