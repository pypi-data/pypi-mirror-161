# acheeve

The repository coordinates multiple chembees. 
A reminder: A chembee object manifests itself through 
the below shown SOLID design pattern. 

Thus, the `acheeve` object handles multiple chembees, for example to evaluate an algorithm: 

![Pattern](acheeve.png)

The above pattern, lets us implement a swarm of chembees for a wide array of endpoints fast. But we only need one API to stick them together. 

The concept is at the moment evaluated by comparing three different datasets (`chembees`). If the method proves valuable, the above pattern will be used for our `SaaS` products.

# Data sets

It turns out data is easily abstracted. However, the `chembee_datasets` module implements the classes in a way that violate the original software pattern. 
Testing the new pattern it turns out, that the imagined SOLID pattern is more useful than the intuition and data operations should indeed not be part of any data class. 

This aligns with knowledge about data modelling. 

# Commercial usage

Currently, we license the software under AGPL 3.0 or later. According to the software pattern, you have to open-source your data when using the package. 

You can easily do so using [veritas-archive](www.veritas-archive.com)
# Cite 

When using the package for your scientific work please cite the repo and the connected papers and thesis work

# References 

* [Publication quality RDKit by proteinsandwavefunctions](https://proteinsandwavefunctions.blogspot.com/2020/12/generating-publication-quality-figures.html)