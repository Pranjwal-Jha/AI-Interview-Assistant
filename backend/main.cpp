#include <bits/stdc++.h>
using namespace std;
class Solution {
public:
  int maxProfit(vector<int> &prices) {
    int start = 0;
    int maxpri = 0;
    for (int i = 0; i < prices.size(); i++) {
      if (prices[i] < prices[start])
        start = i;
      maxpri = max(maxpri, prices[i] - prices[start]);
    }
    return maxpri;
  }
};
