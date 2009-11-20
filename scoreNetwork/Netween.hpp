#ifndef NETWEEN_HPP_9054862562754458964905368042156
#define NETWEEN_HPP_9054862562754458964905368042156

#include "graph/Graph.hpp"
#include <boost/unordered_set.hpp>

class Netween {
private:
    // MEMBERS
    Graph network;
    
    std::string outputFile;
    bool flagAccumulateToInitialNodeScore; // if true, accumulated shortest path score is added to node score
    unordered_set<Vertex> setSeed;

public:
    Netween(); 
    Netween(std::string fileNode, std::string fileEdge, std::string fileOutput, bool flagAccumulateToInitialNodeScore = false);
    ~Netween();
    Graph & getNetwork() { return network; };
    void run(); 
};

#endif // NETWEEN_HPP_
