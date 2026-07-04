#!/usr/bin/env python3
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys


DEFAULT_WIDTH = 900
DEFAULT_HEIGHT = 383


def normalize_with_pillow(input_path, output_path, width, height, quality):
    try:
        from PIL import Image
    except ImportError:
        return False

    with Image.open(input_path) as image:
        image = image.convert("RGB")
        source_ratio = image.width / image.height
        target_ratio = width / height
        if source_ratio > target_ratio:
            new_width = int(image.height * target_ratio)
            left = (image.width - new_width) // 2
            image = image.crop((left, 0, left + new_width, image.height))
        elif source_ratio < target_ratio:
            new_height = int(image.width / target_ratio)
            top = (image.height - new_height) // 2
            image = image.crop((0, top, image.width, top + new_height))
        image = image.resize((width, height), Image.Resampling.LANCZOS)
        image.save(output_path, "JPEG", quality=quality, optimize=True, progressive=True)
    return True


def normalize_with_powershell(input_path, output_path, width, height, quality):
    powershell = shutil.which("powershell") or shutil.which("powershell.exe")
    if not powershell:
        return False

    script = r"""
Add-Type -AssemblyName System.Drawing
$inputPath = [System.IO.Path]::GetFullPath($env:COVER_INPUT)
$outputPath = [System.IO.Path]::GetFullPath($env:COVER_OUTPUT)
$targetW = [int]$env:COVER_WIDTH
$targetH = [int]$env:COVER_HEIGHT
$quality = [int64]$env:COVER_QUALITY
$src = [System.Drawing.Image]::FromFile($inputPath)
try {
  $srcRatio = $src.Width / $src.Height
  $targetRatio = $targetW / $targetH
  if ($srcRatio -gt $targetRatio) {
    $cropH = $src.Height
    $cropW = [int]($src.Height * $targetRatio)
    $cropX = [int](($src.Width - $cropW) / 2)
    $cropY = 0
  } elseif ($srcRatio -lt $targetRatio) {
    $cropW = $src.Width
    $cropH = [int]($src.Width / $targetRatio)
    $cropX = 0
    $cropY = [int](($src.Height - $cropH) / 2)
  } else {
    $cropW = $src.Width
    $cropH = $src.Height
    $cropX = 0
    $cropY = 0
  }
  $bitmap = New-Object System.Drawing.Bitmap($targetW, $targetH, [System.Drawing.Imaging.PixelFormat]::Format24bppRgb)
  try {
    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
    try {
      $graphics.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
      $graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::HighQuality
      $graphics.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality
      $dest = New-Object System.Drawing.Rectangle(0, 0, $targetW, $targetH)
      $crop = New-Object System.Drawing.Rectangle($cropX, $cropY, $cropW, $cropH)
      $graphics.DrawImage($src, $dest, $crop, [System.Drawing.GraphicsUnit]::Pixel)
    } finally {
      $graphics.Dispose()
    }
    $encoder = [System.Drawing.Imaging.ImageCodecInfo]::GetImageEncoders() | Where-Object { $_.MimeType -eq 'image/jpeg' }
    $encoderParams = New-Object System.Drawing.Imaging.EncoderParameters(1)
    $encoderParams.Param[0] = New-Object System.Drawing.Imaging.EncoderParameter([System.Drawing.Imaging.Encoder]::Quality, $quality)
    $bitmap.Save($outputPath, $encoder, $encoderParams)
  } finally {
    $bitmap.Dispose()
  }
} finally {
  $src.Dispose()
}
"""
    env = os.environ.copy()
    env.update(
        {
            "COVER_INPUT": str(input_path),
            "COVER_OUTPUT": str(output_path),
            "COVER_WIDTH": str(width),
            "COVER_HEIGHT": str(height),
            "COVER_QUALITY": str(quality),
        }
    )
    completed = subprocess.run(
        [powershell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
        env=env,
        text=True,
        capture_output=True,
    )
    if completed.returncode != 0:
        sys.stderr.write(completed.stderr)
        return False
    return True


def normalize_with_ffmpeg(input_path, output_path, width, height, quality):
    ffmpeg = shutil.which("ffmpeg") or shutil.which("ffmpeg.exe")
    if not ffmpeg:
        return False

    qscale = max(2, min(31, int((100 - quality) / 3) + 2))
    filter_expr = f"scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height},format=yuvj444p"
    completed = subprocess.run(
        [
            ffmpeg,
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(input_path),
            "-vf",
            filter_expr,
            "-frames:v",
            "1",
            "-q:v",
            str(qscale),
            str(output_path),
        ],
        text=True,
        capture_output=True,
    )
    if completed.returncode != 0:
        sys.stderr.write(completed.stderr)
        return False
    return True


def main():
    parser = argparse.ArgumentParser(description="Normalize a WeChat cover image to 900x383 JPG.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--width", type=int, default=DEFAULT_WIDTH)
    parser.add_argument("--height", type=int, default=DEFAULT_HEIGHT)
    parser.add_argument("--quality", type=int, default=88)
    args = parser.parse_args()

    input_path = Path(args.input).expanduser().resolve()
    output_path = Path(args.output).expanduser().resolve()

    if not input_path.exists():
        raise SystemExit(f"Input image not found: {input_path}")
    if args.width <= 0 or args.height <= 0:
        raise SystemExit("--width and --height must be positive integers.")
    if args.quality < 1 or args.quality > 100:
        raise SystemExit("--quality must be between 1 and 100.")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    if not normalize_with_pillow(input_path, output_path, args.width, args.height, args.quality):
        if not normalize_with_ffmpeg(input_path, output_path, args.width, args.height, args.quality):
            if not normalize_with_powershell(input_path, output_path, args.width, args.height, args.quality):
                raise SystemExit("Image normalization requires Pillow, ffmpeg, or Windows PowerShell System.Drawing support.")

    print(f"Cover image: {output_path}")


if __name__ == "__main__":
    main()
