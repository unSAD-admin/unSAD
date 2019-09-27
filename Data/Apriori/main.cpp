#include <iostream>
#include <fstream>
#include <sstream>
#include "SequenceTree.h"

int main(int argc,char *argv[]) {
    if (argc < 4) {
        std::cout << "Usage ./SubsequenceMining csv_file subsequence_len k_most"
            << std::endl;
    }
    SequenceTree test;
    std::ifstream in;
    in.open(argv[1], std::ios::in);
    std::string line;
    while (std::getline(in, line)) {
        std::vector<int> data;
        std::istringstream iss(line);
        while (!iss.eof()) {
            int num;
            iss >> num;
            data.push_back(num);
        }
        test.countSubsequence(data, std::atoi(argv[2]));
    }
    test.findMostFrequentSubsequence(std::atoi(argv[3]));
    return 0;
}