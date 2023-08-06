# Latent ideology method

Correspondence Analysis applied for calculating 'ideology scores' given an adjacency matrix.

Method for applying the correspondence analysis method for the purpose of calculating 
  an 'ideology score' as stated in [1][2].
  
  -  [1] J. Flamino, A. Galezzi, S. Feldman, M. W. Macy, B. Cross, Z. Zhou, M. Sera
  no, A. Bovet, H. A. Makse, and B. K. Szymanski,
  'Shifting polarization and twitter news influencers between two us presidential elections', 
  arXiv preprint arXiv:2111.02505 (2021).
  
  
  -  [2] Max Falkenberg, Alessandro Galeazzi, Maddalena Torricelli, Niccolo Di Marco, Francesca Larosa, Madalina Sas, Amin Mekacher, 
  Warren Pearce, Fabiana Zollo, Walter Quattrociocchi, Andrea Baronchelli,
  'Growing polarisation around climate change on social media',
  https://doi.org/10.48550/arXiv.2112.12137 (2021).


#How to use

It's simple, just 

```
pip install latent-ideology
```

There are a couple of things you can do here. You can:

-  Make an adjacency matrix given a 'connection dataframe' between targets and sources. (see more in the examples folder in [#Github](https://https://github.com/fedemoss/latent_ideology))
-  Given an adjacency matrix, calculate scores in 1 (or more) dimensions. 
-  Given a 'connection dataframe', you can simple apply the function 'apply_method' and this will generate 2 dataframes: one for the score of the targets and one for the scores of the sources. 
-  Altenatively, you can apply a simplified method by using the function 'apply_simplified_method'. Here, the source's scores are calculating by transposing the adjacency matrix and making reduction of dimensionality following the proccedures of [2].. instead of considering the score of the sources as the mean of the scores of the targets that had interacted with the source. 


*Made with love by **Fede Moss***