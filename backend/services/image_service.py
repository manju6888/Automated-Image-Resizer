import os
import cv2
import numpy as np

class ImageService:
    def __init__(self, upload_folder, output_folder, sr_model):
        self.upload_folder = upload_folder
        self.output_folder = output_folder
        self.sr_model = sr_model

    def process_image(self, filepath, file_id, resize_mode='smart',
                      target_width=None, target_height=None,
                      scale_factor=2.0, maintain_aspect=True,
                      output_format='png', quality=95):

        image = cv2.imread(filepath)
        if image is None:
            raise ValueError("Could not load image")

        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        original_h, original_w = image_rgb.shape[:2]

        print(f"[INFO] Original size: {original_w}x{original_h}")
        print(f"[INFO] Mode: {resize_mode}, Scale: {scale_factor}, W: {target_width}, H: {target_height}")

        # Decide target size
        if resize_mode == 'percentage' or resize_mode == 'super_resolution':
            tw = int(original_w * float(scale_factor))
            th = int(original_h * float(scale_factor))
        elif target_width or target_height:
            tw = int(target_width) if target_width else original_w
            th = int(target_height) if target_height else original_h
            if maintain_aspect:
                ratio_w = tw / original_w
                ratio_h = th / original_h
                ratio = min(ratio_w, ratio_h)
                tw = int(original_w * ratio)
                th = int(original_h * ratio)
        else:
            # Default: use scale_factor
            tw = int(original_w * float(scale_factor))
            th = int(original_h * float(scale_factor))

        # Minimum 1px
        tw = max(1, tw)
        th = max(1, th)

        print(f"[INFO] Target size: {tw}x{th}")

        # Resize
        if tw > original_w or th > original_h:
            # Upscale
            result = cv2.resize(image_rgb, (tw, th), interpolation=cv2.INTER_CUBIC)
            # Light sharpen
            kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
            result = cv2.filter2D(result, -1, kernel)
            result = np.clip(result, 0, 255).astype(np.uint8)
        else:
            # Downscale
            result = cv2.resize(image_rgb, (tw, th), interpolation=cv2.INTER_AREA)

        result_h, result_w = result.shape[:2]
        print(f"[INFO] Result size: {result_w}x{result_h}")

        # Save
        output_filename = f"{file_id}_resized.{output_format}"
        output_path = os.path.join(self.output_folder, output_filename)
        result_bgr = cv2.cvtColor(result, cv2.COLOR_RGB2BGR)

        if output_format.lower() in ('jpg', 'jpeg'):
            cv2.imwrite(output_path, result_bgr, [cv2.IMWRITE_JPEG_QUALITY, int(quality)])
        else:
            cv2.imwrite(output_path, result_bgr)

        print(f"[INFO] Saved: {output_path}")

        return {
            'original_dimensions': {'width': original_w, 'height': original_h},
            'result_dimensions': {'width': result_w, 'height': result_h},
            'original_size_mb': round(os.path.getsize(filepath) / (1024 * 1024), 3),
            'output_size_mb': round(os.path.getsize(output_path) / (1024 * 1024), 3),
            'scale_applied': round(result_w / original_w, 2),
            'output_format': output_format,
            'resize_mode': resize_mode,
            'output_filename': output_filename,
            'download_url': f'/api/download/{file_id}',
            'preview_url': f'/api/preview/{file_id}'
        }