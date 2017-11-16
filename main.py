# ===================================
# Import the libraries
# ===================================
import numpy as np
from matplotlib import pylab as plt
import imaging
import utility
import os,sys

# ===================================
# Which stages to run
# ===================================
do_add_noise = False #True
do_black_level_correction = True
do_lens_shading_correction = False #True
do_bad_pixel_correction = False #True
do_channel_gain_white_balance = True
do_bayer_denoise = False #True
do_demosaic = True
do_demosaic_artifact_reduction = False #True
do_color_correction = True
do_gamma = True
do_tone_mapping = False #True
do_memory_color_enhancement = False
do_noise_reduction = False
do_sharpening = False
do_distortion_correction = False

# ===================================
# Remove all the .png files
os.system("rm images/*.png")
# ===================================

# ===================================
# raw image and set up the metadata
# ===================================
# uncomment the image_name to run it via pipeline
image_name = "DSC_1339_768x512_rggb"        # image content: Rose
# image_name = "DSC_1320_2048x2048_rggb"      # image content: Potrait

# read the raw image
temp = np.fromfile("images/" + image_name + ".raw", dtype="uint16", sep="")


if (image_name == "DSC_1339_768x512_rggb"):

    temp = temp.reshape([512, 768])
    raw = imaging.ImageInfo("1339_768x512_rggb", temp)
    raw.set_color_space("raw")
    raw.set_bayer_pattern("rggb")
    raw.set_channel_gain((1.94921875, 1.0, 1.0, 1.34375)) # Please shuffle the values
                                                          # depending on bayer_pattern
    raw.set_bit_depth(14)
    raw.set_black_level((600, 600, 600, 600))
    raw.set_white_level((15520, 15520, 15520, 15520))
    # the ColorMatrix2 found from the metadata
    raw.set_color_matrix([[.9020, -.2890, -.0715],\
                          [-.4535, 1.2436, .2348],\
                          [-.0934, .1919,  .7086]])

elif (image_name == "DSC_1320_2048x2048_rggb"):

    temp = temp.reshape([2048, 2048])
    raw = imaging.ImageInfo("1320_2048x2048_rggb", temp)
    raw.set_color_space("raw")
    raw.set_bayer_pattern("rggb")
    raw.set_channel_gain((1.94921875, 1.0, 1.0, 1.34375)) # Please shuffle the values
                                                          # depending on bayer_pattern
    raw.set_bit_depth(14)
    raw.set_black_level((600, 600, 600, 600))
    raw.set_white_level((15520, 15520, 15520, 15520))
    # the ColotMatrix2 found from the metadata
    raw.set_color_matrix([[.9020, -.2890, -.0715],\
                          [-.4535, 1.2436, .2348],\
                          [-.0934, .1919,  .7086]])

else:
    print("Warning! image_name not recognized.")


data = raw.data

# ===================================
# Add noise
# ===================================
if do_add_noise:
    noise_mean = 0
    noise_standard_deviation = 100
    seed = 100
    clip_range = [600, 65535]
    data = utility.synthetic_image_generate(\
    raw.get_width(), raw.get_height()).create_noisy_image(\
    data, noise_mean, noise_standard_deviation, seed, clip_range)
else:
    pass

# ===================================
# Black level correction
# ===================================
if do_black_level_correction:
    data = imaging.black_level_correction(data, \
                                          raw.get_black_level(),\
                                          raw.get_white_level(),\
                                          [0, 2**raw.get_bit_depth() - 1])
    utility.imsave(data, "images/" + image_name + "_out_black_level_correction.png", "uint16")
else:
    pass

# ===================================
# Lens shading correction
# ===================================
if do_lens_shading_correction:
    # normally dark_current_image and flat_field_image are
    # captured in the image quality lab using flat field chart
    # here we are synthetically generating thouse two images
    dark_current_image, flat_field_image = utility.synthetic_image_generate(\
    raw.get_width(), raw.get_height()).create_lens_shading_correction_images(\
                                    0, 65535, 40000)

    # save the dark_current_image and flat_field_image for viewing
    utility.imsave(dark_current_image, "images/" + image_name + "_dark_current_image.png", "uint16")
    utility.imsave(flat_field_image, "images/" + image_name + "_flat_field_image.png", "uint16")

    data = imaging.lens_shading_correction(data).flat_field_compensation(\
    dark_current_image, flat_field_image)

    # data = lsc.approximate_mathematical_compensation([0.01759, -28.37, -13.36])
    utility.imsave(data, "images/" + image_name + "_out_lens_shading_correction.png", "uint16")

else:
    pass

# ===================================
# Bad pixel correction
# ===================================
if do_bad_pixel_correction:
    neighborhood_size = 3
    data = imaging.bad_pixel_correction(data, neighborhood_size)
    utility.imsave(data, "images/" + image_name + "_out_bad_pixel_correction.png", "uint16")
else:
    pass

# ===================================
# Channel gain for white balance
# ===================================
if do_channel_gain_white_balance:
    data = imaging.channel_gain_white_balance(data,\
                                              raw.get_channel_gain())
    utility.imsave(data, "images/" + image_name + "_out_channel_gain_white_balance.png", "uint16")
else:
    pass

# ===================================
# Bayer denoising
# ===================================
if do_bayer_denoise:

    # bayer denoising parameters
    neighborhood_size = 5
    initial_noise_level = 65535 * 10 / 100
    hvs_min = 1000
    hvs_max = 2000
    clip_range = [0, 65535]
    threshold_red_blue = 1300

    # data is the denoised output, ignoring the second output
    data, _ = imaging.bayer_denoising(data).utilize_hvs_behavior(\
    raw.get_bayer_pattern(), initial_noise_level, hvs_min, hvs_max, threshold_red_blue, clip_range)

    utility.imsave(data, "images/" + image_name + "_out_bayer_denoising.png", "uint16")
    # utility.imsave(np.clip(texture_degree_debug*65535, 0, 65535), "images/" + image_name + "_out_texture_degree_debug.png", "uint16")

else:
    pass

# ===================================
# Demosacing
# ===================================
if do_demosaic:
    data = imaging.demosaic(data, raw.get_bayer_pattern()).mhc(False)
    utility.imsave(data, "images/" + image_name + "_out_demosaic.png", "uint16")
else:
    pass

# ===================================
# Demosaic artifact reduction
# ===================================
if do_demosaic_artifact_reduction:
    # data = imaging.demosaic(data).post_process_local_color_ratio(0.80 * 65535)
    # utility.imsave(data, "images/" + image_name + "_out_local_color_ratio.png", "uint16")

    edge_detection_kernel_size = 5
    edge_threshold = 0.05
    data, edge_location = imaging.demosaic(data).post_process_median_filter(edge_detection_kernel_size, edge_threshold)
    utility.imsave(data, "images/" + image_name + "_out_median_filter.png", "uint16")
    utility.imsave(edge_location*65535, "images/" + image_name + "_edge_location.png", "uint16")
else:
    pass


# ===================================
# Color correction
# ===================================
if do_color_correction:
    data = imaging.color_correction(data, raw.get_color_matrix()).apply_cmatrix()
    utility.imsave(data, "images/" + image_name + "_out_color_correction.png", "uint16")
else:
    pass

# ===================================
# Gamma
# ===================================
if do_gamma:

    # by value
    #data = imaging.nonlinearity(data, "gamma").by_value(1/2.2, [0, 65535])

    # by table
    data = imaging.nonlinearity(data, "gamma").by_table("tables/GammaE.txt", "gamma", [0, 65535])

    utility.imsave(data, "images/" + image_name + "_out_gamma.png", "uint16")

else:
    pass


# ===================================
# Chromatic aberration correction
# ===================================

# ===================================
# Tone mapping
# ===================================
if do_tone_mapping:
    data = imaging.tone_mapping(data).nonlinear_masking(1.0)

    utility.imsave(data, "images/" + image_name + "_out_tone_mapping.png", "uint16")

else:
    pass


# ===================================
# Memory color enhancement
# ===================================
if do_memory_color_enhancement:

    target_hue = [30., -115., 100.]
    hue_preference = [45., -90., 130.]
    hue_sigma = [20., 10., 5.]
    is_both_side = [True, False, False]
    multiplier = [0.6, 0.6, 0.6]
    chroma_preference = [25., 17., 30.]
    chroma_sigma = [10., 10., 5.]

    data = imaging.memory_color_enhancement(data).by_hue_squeeze(target_hue,\
                                                                 hue_preference,\
                                                                 hue_sigma,\
                                                                 is_both_side,\
                                                                 multiplier,\
                                                                 chroma_preference,\
                                                                 chroma_sigma)

    utility.imsave(data, "images/" + image_name + "_out_memory_color_enhancement.png", "uint16")

else:
    pass


# ===================================
# Noise reduction
# ===================================
if do_noise_reduction:

    # sigma filter parameters
    neighborhood_size = 7
    sigma = [1000, 500, 500]
    data = imaging.noise_reduction(data).sigma_filter(neighborhood_size, sigma)

    utility.imsave(data, "images/" + image_name + "_out_noise_reduction.png", "uint16")

else:
    pass

# ===================================
# Sharpening
# ===================================
if do_sharpening:

    data = imaging.sharpening(data).unsharp_masking()

    utility.imsave(data, "images/" + image_name + "_out_sharpening.png", "uint16")

else:
    pass

# ===================================
# Distortion correction
# ===================================
if do_distortion_correction:

    correction_type="barrel-1"
    strength=0.5
    zoom_type="fit"
    clip_range=[0, 65535]

    data = imaging.distortion_correction(data).empirical_correction(correction_type, strength, zoom_type, clip_range)
    utility.imsave(data, "images/" + image_name + "_out_distortion_correction.png", "uint16")

else:
    pass
