# renal-segmentation

Automatic Renal Segmentation for MR Urography Using 3D-GrabCut and Random Forests

This is the implementation of the algorithm described in the following paper:

>[Yoruk, U., Hargreaves, B. A. and Vasanawala, S. S. (2018), Automatic renal segmentation for MR urography using 3D-GrabCut and random forests. Magn. Reson. Med, 79: 1696–1707. doi:10.1002/mrm.26806](http://onlinelibrary.wiley.com/doi/10.1002/mrm.26806/full)

The source code is located in GitHub repository:

https://github.com/umityoruk/renal-segmentation



The easiest way to run/test this algorithm is the docker image located in Docker Hub:

https://hub.docker.com/r/umityoruk/renal-segmentation/



Run the docker image using:

```

docker run -it --rm -v /path/to/local/dir:/data -p 8888:8888 umityoruk/renal-segmentation

```

The image starts the jupyter notebook server at port 8888. You can access the notebook by using the link provided in the terminal. The path `/path/to/local/dir` is a directory on the host machine that is mounted as `/data` on the docker container. If you put your dicom images in this directory, you can access them from the Jupyter Notebook running inside the docker container.



See "/Notebook/Automatic\_Segmentation\_Example.ipynb" for usage examples.



To stop the image simply hit `Ctrl-C` twice in the terminal.



If you want to process dicom images directly without using the notebook you can run the python command directly:

```

docker run --rm  -v /path/to/local/dir:/data umityoruk/renal-segmentation "python renalSegment.py /data/DicomIn /data/DicomOut"

```

The example above assumes that the dicom images are stored in `/path/to/local/dir/DicomIn` and the output folder `DicomOut` is the last parameter to the renalSegment script.  


