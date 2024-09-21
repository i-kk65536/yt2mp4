import argparse

import flet as ft

class Dialog(ft.UserControl):
    def __init__(self, show_message: str):
        super().__init__()
        self.text_message = ft.Text(
            value=show_message,
        )
        self.button_exit = ft.ElevatedButton(
            text="OK",
            on_click=self.exit_clicked,
        )

    def build(self):
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Container(
                                content=self.text_message,
                                expand=True
                            )
                        ],
                    ),
                    ft.Row(
                        controls=[
                            self.button_exit,
                        ],
                        alignment=ft.MainAxisAlignment.END,
                    ),
                ],
            ),
            padding=10,
        )

    def exit_clicked(self, event: ft.ControlEvent) -> None:
        self.page.window_destroy()

def runDialog(title: str, message: str) -> None:
    def dialog(page: ft.Page, title: str, message: str) -> None:
        page.title = title
        page.window_width = 256
        page.window_height = 144
        page.theme = ft.Theme(font_family="源ノ角ゴシック Code JP")
        page.window_always_on_top = True

        view = Dialog(show_message=message)
        
        page.add(view)

    ft.app(target=lambda page: dialog(page, title, message))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("title")
    parser.add_argument("message")
    args = parser.parse_args()

    runDialog(args.title, args.message)

if __name__ == "__main__":
    main()