from abc import ABC, abstractmethod
from dataclasses import dataclass
import json

import yaml

from evalgen.llm import invoke
from evalgen.prompts import evaluate as eval_prompt


@dataclass
class EvalBase(ABC):
    name: str
    description: str

    @abstractmethod
    def eval(self, response: str, context: str) -> bool:
        pass

    @abstractmethod
    def to_dict(self) -> dict:
        pass

    @classmethod
    def from_dict(cls, d: dict) -> "EvalBase":
        if d["type"] == "computed":
            return ComputedEval.from_dict(d)
        elif d["type"] == "llm_assisted":
            return LLMAssistedEval.from_dict(d)
        else:
            raise ValueError("Unknown eval type")

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, s: str) -> "EvalBase":
        return cls.from_dict(json.loads(s))

    def to_yaml(self) -> str:
        return yaml.dump(self.to_dict())

    @classmethod
    def from_yaml(cls, s: str) -> "EvalBase":
        return cls.from_dict(yaml.safe_load(s))


@dataclass
class ComputedEval(EvalBase):
    _type: str = "computed"
    code: str

    def eval(self, prompt: str, response: str) -> bool:
        local_context = {"prompt": prompt, "response": response}
        exec(self.code, {}, local_context)

        if not isinstance(local_context["result"], bool):
            raise ValueError("result must be a boolean")

        return local_context["result"]

    def to_dict(self) -> dict:
        return {
            "type": self._type,
            "name": self.name,
            "description": self.description,
            "code": self.code,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "ComputedEval":
        return cls(
            name=d["name"],
            description=d["description"],
            code=d["code"],
        )


@dataclass
class LLMAssistedEval(EvalBase):
    _type: str = "llm_assisted"
    assertion: str

    def eval(self, prompt: str, response: str) -> bool:
        _ = prompt  # unused for now

        response = invoke(
            messages=[
                {"role": "system", "content": eval_prompt.system.render()},
                {
                    "role": "user",
                    "content": eval_prompt.user.render(
                        response=response,
                        criteria=self.assertion,
                    ),
                },
            ],
        )

        aliases = {
            # true
            "true": True,
            "yes": True,
            "correct": True,
            "1": True,
            "y": True,
            # false
            "false": False,
            "no": False,
            "incorrect": False,
            "0": False,
            "n": False,
        }
        result = aliases.get(response.lower().strip())

        if result is None:
            raise ValueError(f"Invalid response: {response}")

        return result

    def to_dict(self) -> dict:
        return {
            "type": self._type,
            "name": self.name,
            "description": self.description,
            "prompt": self.prompt,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "LLMAssistedEval":
        return cls(
            name=d["name"],
            description=d["description"],
            model_name=d["model_name"],
            model_version=d["model_version"],
            model_input=d["model_input"],
        )
