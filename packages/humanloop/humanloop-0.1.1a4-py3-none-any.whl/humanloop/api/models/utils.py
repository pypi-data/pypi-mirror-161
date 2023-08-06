from pydantic import BaseModel


class RootBaseModel(BaseModel):
    def dict(self, **kwargs):
        output = super().dict(**kwargs)
        return output["__root__"]
