import flet as ft

from component import Body

def runApp() -> None:
    def app(page: ft.Page) -> None:
        page.title = "YouTube -2- mp4"
        page.window_width = 1024
        page.window_height = 768
        page.theme = ft.Theme(font_family="源ノ角ゴシック Code JP")
        
        view = Body()

        page.add(view)

    ft.app(target=app)

def main():
    runApp()

if __name__ == "__main__":
    main()