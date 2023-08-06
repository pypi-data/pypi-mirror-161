import inspect
from typing import Callable, ClassVar, Type, TypeVar

from fastapi import APIRouter, Depends, Request
from wtforms import Form

from .controller import Controller


async def _extract_form_data(request: Request):
    return await request.form()


def _copy_dependencies(source_function: Callable, dest_function: Callable):
    source_signature = inspect.signature(source_function)
    dest_signature = inspect.signature(dest_function)
    _, _, *params_to_copy = source_signature.parameters.values()  # ignore `self` and `form_data` parameters
    existing_params = [v for v in dest_signature.parameters.values() if v.kind != inspect.Parameter.VAR_KEYWORD]
    dest_function.__signature__ = dest_signature.replace(parameters=existing_params + params_to_copy)
    return dest_function


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

        def on_valid_form(self, form: MyForm, value = Depends(some_other_dependency)):
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
            def handle_form_page(self, form_data=Depends(_extract_form_data), **kw):
                form = cls.form(formdata=form_data)
                if not form.validate():
                    return self.render(cls.template, context={"form": form})
                return self.on_valid_form(form, **kw)

            cls.main_page = main_page
            cls.handle_form_page = _copy_dependencies(cls.on_valid_form, handle_form_page)

        super().__init_subclass__(router=router, **kwargs)

    def on_valid_form(self, *args, **kwargs):
        """
        Override this method to handle the form data
        """
