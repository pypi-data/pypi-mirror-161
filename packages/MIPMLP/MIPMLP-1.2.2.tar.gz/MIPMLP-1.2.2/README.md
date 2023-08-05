
## Preprocessing for 16S values.
The input file for the preprocessing should contain detailed unnormalized OTU/Feature values as a biom table, the appropriate taxonomy as a tsv file,
and a possible tag file, with the class of each sample.
The tag file is not used for the preprocessing, but is used to provide some statistics on the relation between the features and the class.
You can also run the preprocessing without a tag file.  
### input                                                               
Here is an example of how the input OTU file should look like : ([file example](https://mip-mlp.math.biu.ac.il/download-example-files))

<img src="https://drive.google.com/uc?export=view&id=18s12Zxc4nOHjk0vr8YG8YQGDU0D8g7wp" alt="drawing" width="400" height="450"/>

### Parameters to the preprocessing
Now you will have to select the parameters for the preprocessing.
1. The taxonomy level used - taxonomy sensitive dimension reduction by grouping the bacteria at
 a given taxonomy level. All features with a given representation at a given taxonomy
 level will be grouped and merged using three different methods: Average, Sum or Merge (using PCA then followed by normalization).
2. Normalization - after the grouping process, you can apply two different normalization methods. the first one is the log (10 base)scale. in this method <br/>
x → log10(x + ɛ),where ɛ is a minimal value to prevent log of zero values. <br/>
The second methos is to normalize each bacteria through its relative frequency.<br/>
> If you chose the Log normalization, you now have four standardization <br/>possibilities:<br/>
> a) No standardization<br/>
> b) Z-score each sample<br/>
> c) Z-score each bacteria<br/>
> d) Z-score each sample, and Z-score each bacteria (in this order)<br/>
When performing relative normalization, we either dont standardize the results
or performe only a standardization on the bacteria.<br/>
3. Dimension reduction - after the grouping, normalization and standardization you can choose from two Dimension reduction method: PCA or ICA. If you chose to apply a Dimension reduction method, you will also have to decide the number of dimensions you want to leave.


### How to use
use MIPMLP.preprocess(input_df)
####parameters:
taxonomy_level 4-7 , default is 7<br/>
taxnomy_group : sub PCA, mean, sum, default is mean<br/>
epsilon: 0-1<br/>
z_scoring: row, col, both, No, default is No<br/>
pca: (0, 'PCA') second element always PCA. first is 0/1<br/>
normalization: log, relative, default is log<br/>
norm_after_rel: No, relative, default is No<br/>

### output
The output is the processed file.

<img src="https://drive.google.com/uc?export=view&id=1UPdJfUs_ZhuWFaHmTGP26gD3i2NFQCq6" alt="drawing" width="400" height="400"/>

## iMic 
 iMic is a  method to combine information from different taxa and improves data representation for machine learning using microbial taxonomy. 
iMic translate the microbiome to images, and convolutional neural networks are then applied to the image.

### micro2matrix
Translates the microbiome values and the taxonomy tree into an image. micro2matrix also save the images that were created in a guven folder.
#### input
A pandas dataframe which is similar to the MIPMLP preprocessing's input.

A folder to save the new images at.

#### Parameters
You can determine all the MIPMLP preprocessing parameters too, otherwise it will run with its deafulting parameters.

#### How to use
	import pandas as pd
	df = pd.read_csv("address/ASVS_file.csv")
    folder = "save_img_folder"
    MIPMLP.micro2matrix(df, folder)

### CNN2 class - optional
A model of 2 convolutional layer followed by 2 fully connected layers.

####CNN model parameters
l1 loss = the coefficient of the L1 loss

weight decay = L2 regularization

lr = learning rate

batch size = as it sounds
    
activation = activation function one of:  "elu", | "relu" | "tanh"
    
dropout = as it sounds (is common to all the layers)

kernel_size_a = the size of the kernel of the first CNN layer (rows)

kernel_size_b = the size of the kernel of the first CNN layer (columns)

stride = the stride's size of the first CNN
    
padding = the padding size of the first CNN layer
    
padding_2 = the padding size of the second CNN layer
    
kernel_size_a_2 = the size of the kernel of the second CNN layer (rows)
    
kernel_size_b_2 = the size of the kernel of the second CNN layer (columns)
    
stride_2 = the stride size of the second CNN
    
channels = number of channels of the first CNN layer
    
channels_2 = number of channels of the second CNN layer
    
linear_dim_divider_1 = the number to divide the original input size to get the number of neurons in the first FCN layer
    
linear_dim_divider_2 = the number to divide the original input size to get the number of neurons in the second FCN layer

input dim = the dimention of the input image (height, weight)
#### How to use
	params = {
        "l1_loss": 0.1,
        "weight_decay": 0.01,
        "lr": 0.001,
        "batch_size": 128,
        "activation": "elu",
        "dropout": 0.1,
        "kernel_size_a": 4,
        "kernel_size_b": 4,
        "stride": 2,
        "padding": 3,
        "padding_2": 0,
        "kernel_size_a_2": 2,
        "kernel_size_b_2": 7,
        "stride_2": 3,
        "channels": 3,
        "channels_2": 14,
        "linear_dim_divider_1": 10,
        "linear_dim_divider_2": 6,
		"input_dim": (8,100)
    }
    model = MIPMLP.CNN(params)

A trainer on the model should be applied by the user.

# Citation

Oshrit, Shtossel, et al. "Image and graph convolution networks improve microbiome-based machine learning accuracy." arXiv preprint arXiv:2205.06525 (2022).‏

