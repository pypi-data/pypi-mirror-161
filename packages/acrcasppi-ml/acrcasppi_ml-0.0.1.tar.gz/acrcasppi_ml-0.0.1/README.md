
acrcasppi_ml predicts protein-protein interaction between Anti-CRISPR protein (Acr) and CRISPR-associated protein (Cas), 
based on the machine learning algorithm.

***Input file:***
The user need to provide pairs of acr and cas protein as input. The first and second column should contain acr and cas 
protein, respecticely.
An example input file can be obtained from the given link https://github.com/snehaiasri/acrcasppi/blob/main/example.csv.

***Usage:***
After installation, perform the following steps to use the package

*import the package*
>import acrcasppi_ml as acp

*save the input file as dataframe. Provide the full path of the input file.*
> df = pd.read_csv("example.csv")

*convert the df into numpy array*
> var = df.to_numpy()

*call the predict function*
> x = acp.predict(var)

*to call the predict_proba function*
> y = acp.predict_proba(var)

*call gen_file function to generate the output file (output.txt) in your current working directory*
> acp.gen_file(var)

***Help***
To see the documentation of each function, use help command. For example, help(acr_cas_ppi) or help(predict).

***Requirments***
Python >3.9,
numpy,
pickle-mixin,
sklearn.




