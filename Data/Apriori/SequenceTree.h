#ifndef SUBSEQUENCEMINING_SEQUENCETREE_H
#define SUBSEQUENCEMINING_SEQUENCETREE_H

#include <map>
#include <vector>
#include <queue>
#include <iostream>

class SequenceTree {
private:
    struct Node {
        std::vector<int> action;
        int freq;
        std::map<int, Node> children;

        Node() : action({}), freq(0) {}

        Node(Node *n, int a) : action(n->action), freq(0) {
            action.push_back(a);
        }

        Node *find_children(int action) {
            auto it = children.find(action);
            if (it == children.end()) {
                children.insert({action, Node(this, action)});
            }
            return &children[action];
        }
    };

    Node* root;
    std::function<bool(Node*, Node*)> comp = [](Node *a, Node *b){
        return a->freq < b->freq;
    };

    typedef std::priority_queue<Node*, std::vector<Node*>, decltype(comp)> nodequeue_t;
    nodequeue_t q;

    void traverseTree(Node *node) {
        if (node->children.empty()) {
            q.push(node);
            return;
        }
        for (auto &child : node->children) {
            traverseTree(&child.second);
        }
    }

public:
    SequenceTree() {
        root = new Node();
        q = nodequeue_t(comp);
    }

    ~SequenceTree() { delete(root); }

    void countSubsequence(const std::vector<int> &data, int len) {
        for (int action : data) {
            Node *node = root->find_children(action);
        }
        for (int i = 0; i < static_cast<int>(data.size()) - len; i++) {
            Node *node = root->find_children(data[i]);
            for (int j = 1; j <= len; j++) {
                node = node->find_children(data[i + j]);
            }
            node->freq++;
        }
    }

    void findMostFrequentSubsequence(int k) {
        traverseTree(root);
        for (int i = 0; i < k; i++) {
            Node *node = q.top();
            q.pop();
            std::cout << "(";
            for (auto a : node->action) {
                std::cout << a << ", ";
            }
            std::cout << "): " << node->freq << std::endl;
        }
    }
};


#endif //SUBSEQUENCEMINING_SEQUENCETREE_H
