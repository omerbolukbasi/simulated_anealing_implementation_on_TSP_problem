## SIMULATED ANEALING IMPLEMENTATION ON TRAVELLING SALESMAN PROBLEM
<br>
Genetic Simulated Anealing(SA) algorithm is implemented on Travelling Salesman Problem. Performance comparison of SA and a given Genetic Algorithm(GA) is done over a given TSP topology.

## Simulated Anealing Algorithm<br>

Simulated Annealing(SA) mimics the physical annealing process. In the physical process material is 
heated and slowly cooled towards a strong crystalline structure instead of metastable states. [1]
In SA, for a calculated probability the solutions worse than the best solutions are also accepted. This 
property is used to explore different areas in search space. In addition, the solutions better than the 
best solution are also accepted. The acceptance probability calculation is based on T: Existing 
Temperature, 𝑒𝑣𝑎𝑙(𝑣𝑛): fitness of the existing individual, 𝑒𝑣𝑎𝑙(𝑣𝑐): fitness of the child individual.

![image](https://user-images.githubusercontent.com/44832162/147351876-23dcaf9d-7a37-4faf-810a-71400069f55d.png)

In the beginning of the search T is large. If T is large then the probability of accepting worse solution 
is also high which yields the algorithm acts as a random search (Accepts most of the incoming 
solutions). In the end of the search T is small. If T is small then SA acts as a local search because it 
accepts mostly the best solutions.

Temperature decrements whether linear:<br>
![image](https://user-images.githubusercontent.com/44832162/147352038-bb7acd27-927b-42ae-829d-64fc5e6b774b.png)
<br>
or geometric:<br>
![image](https://user-images.githubusercontent.com/44832162/147352055-339ea77d-035b-4d24-a1a4-a2d15126bb53.png)
<br>
