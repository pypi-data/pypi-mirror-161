from typing import ClassVar, Type, TypeVar

from fastapi import APIRouter, Depends, Request
from wtforms import Form

from .controller import Controller


async def _extract_form_data(request: Request):
    return await request.form()


FormT = TypeVar("FormT", bound=Form)


class FormController(Controller):
    """
    Base class allowing to write controllers to handle forms

    Example:
    ```
    class MyClass(FormController, MyJinjaController, router=router):
        url = "/my_form"
        template = "form.html"
        form = MyForm

        def on_valid_form(self, form: MyForm):
            return "OK"
    ```
    """

    url: ClassVar[str]
    template: ClassVar[str]
    form: ClassVar[Type[FormT]]

    def __init_subclass__(cls, router: APIRouter = None, **kwargs):
        if router is not None:
            @router.get(cls.url)
            def main_page(self):
                return self.render(cls.template, context={"form": cls.form()})

            @router.post(cls.url)
            def handle_form_page(self, form_data=Depends(_extract_form_data)):
                form = cls.form(formdata=form_data)
                if not form.validate():
                    return self.render(cls.template, context={"form": form})
                return self.on_valid_form(form)

            cls.main_page = main_page
            cls.handle_form_page = handle_form_page

        super().__init_subclass__(router=router, **kwargs)
