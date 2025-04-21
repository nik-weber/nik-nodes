# Importação dos nodes
from .nodes.VideoPicker import VideoPicker
from .nodes.ImagePicker import ImagePicker
from .nodes.ImageAdjustments import ImageAdjustments
from .nodes.SubtitleNode import SubtitleNode
from .node_select_frames_by_target_fps import SelectFramesByTargetFPS  # novo node

# Mapeamento das classes dos nodes
NODE_CLASS_MAPPINGS = {
    "VideoPicker": VideoPicker,
    "ImagePicker": ImagePicker,
    "ImageAdjustments": ImageAdjustments,
    "SubtitleNode": SubtitleNode,
    "SelectFramesByTargetFPS": SelectFramesByTargetFPS 
}

# Mapeamento dos nomes exibidos para os nodes
NODE_DISPLAY_NAME_MAPPINGS = {
    "VideoPicker": "🧪 Video Picker",
    "ImagePicker": "🧪 Image Picker",
    "ImageAdjustments": "🧪 Image Adjustments",
    "SubtitleNode": "🧪 Caption Generator",
    "SelectFramesByTargetFPS": "🎞️ Select Frames by Target FPS"  # novo
}

# Impressão estilizada de carregamento bem-sucedido
print("\033[92m" + """

    _           _   _   _           _    
   (_) _       (_) (_) (_)       _ (_)   
   (_)(_)_     (_) (_) (_)    _ (_)      
   (_)  (_)_   (_) (_) (_) _ (_)         
   (_)    (_)_ (_) (_) (_)(_) _          
   (_)      (_)(_)     (_)   (_) _       
   (_)         (_)  _  (_)      (_) _    
   (_)         (_) (_) (_)         (_)   
                                          
   Custom Nodes Carregados com Sucesso! 🚀

""" + "\033[0m")
