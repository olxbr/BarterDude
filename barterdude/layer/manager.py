from barterdude.layer import Layer


class LayerManager:
    def __init__(self):
        self._layers = {}

    def __str__(self):
        to_str = ""
        for identifier in self._layers.items():
            to_str += f"{identifier}:\n"
            for idx, layer in enumerate(self._layers.get(identifier, [])):
                to_str += f"Layer {idx+1}: "
                to_str += ", ".join(layer.hooks)
                to_str += "\n"
            to_str += "\n"

        return to_str

    def new(self, identifier: str):
        return Layer(identifier)

    def store(self, layer: Layer):
        self._layers.setdefault(layer.identifier, [])
        self._layers[layer.identifier].append(layer)

    def get(self, identifier: str):
        return self._layers.get(identifier, [])
