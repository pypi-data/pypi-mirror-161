try:
    from amulet.api.block import Block
except ModuleNotFoundError:
    from minecraft_model_reader.api.amulet.block import Block

from .mesh.block.block_mesh import BlockMesh
