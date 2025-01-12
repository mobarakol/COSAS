import json
import os

import warnings

import SimpleITK
import torch

from mmseg.apis import inference_model, init_model
#from segment_anything import sam_model_registry, SamPredictor

def read(path):
    image = SimpleITK.ReadImage(path)
    return SimpleITK.GetArrayFromImage(image)
  

def write(path, array):
    image = SimpleITK.GetImageFromArray(array)
    SimpleITK.WriteImage(image, path, useCompression=False)


# def main():
#     input_root = '/input/images/adenocarcinoma-image'
#     output_root = '/output/images/adenocarcinoma-mask'

#     if not os.path.exists(output_root):
#         os.makedirs(output_root)

#     config = 'config.py'
#     checkpoint = 'checkpoint.pth'
#     model = init_model(config, checkpoint, device='cuda:0')
    
#     with torch.no_grad():
#         for filename in os.listdir(input_root):
#             if filename.endswith('.mha'):
#                 output_path = f'{output_root}/{filename}'
#                 try:
#                     input_path = input_root + '/' + filename
#                     image = read(input_path)
#                     result = inference_model(model, image).pred_sem_seg.cpu().data
#                     write(output_path, result.squeeze().numpy().astype('uint8'))
#                 except Exception as error:
#                     print(error)

def main():
    input_root = '/input/images/adenocarcinoma-image'
    output_root = '/output/images/adenocarcinoma-mask'

    if not os.path.exists(output_root):
        os.makedirs(output_root)

    sam_checkpoint = 'PtiSAM/checkpoints/sam_vit_b_01ec64.pth'
    lora_checkpoint = 'PtiSAM/checkpoints/epoch_159.pth'

    device = 'cuda' if torch.cuda.is_available() else 'cpu'

    # Load the SAM model
    sam = sam_model_registry["vit_b"](checkpoint=sam_checkpoint)
    sam.to(device=device)

    # Load the LoRA checkpoint
    lora_state_dict = torch.load(lora_checkpoint)
    sam.load_state_dict(lora_state_dict, strict=False)

    # Create a SamPredictor instance
    predictor = SamPredictor(sam)

    with torch.no_grad():
        for filename in os.listdir(input_root):
            if filename.endswith('.mha'):
                output_path = f'{output_root}/{filename}'
                try:
                    input_path = input_root + '/' + filename
                    image = read(input_path)

                    # Set the image for the predictor
                    predictor.set_image(image)

                    # Generate masks (adjust the parameters as needed)
                    masks, _, _ = predictor.predict(
                        point_coords=None,
                        point_labels=None,
                        multimask_output=False,
                    )

                    # Save the generated mask
                    write(output_path, masks[0].astype('uint8'))

                except Exception as error:
                    print(error)
                    
                    
if __name__ == '__main__':
    main()