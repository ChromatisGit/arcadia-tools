//By Rafael Soares https://stackoverflow.com/questions/5919298/algorithm-for-finding-the-fewest-rectangles-to-cover-a-set-of-rectangles-without

#include <iostream>
#include <string>

#define MAX 32

int tab[MAX][MAX];
int N, M;
int sumed[MAX][MAX];
int resp[MAX][MAX][MAX][MAX];
bool exist[MAX][MAX][MAX][MAX];

int t(int x, int y) {
    if (x < 0 || y < 0) return 0;
    return sumed[x][y];
}

int subrec(int x1, int y1, int x2, int y2) {
    return t(x2, y2) - t(x2, y1 - 1) - t(x1 - 1, y2) + t(x1 - 1, y1 - 1);
}

int dp(int x1, int y1, int x2, int y2) {
    if (exist[x1][y1][x2][y2]) return resp[x1][y1][x2][y2];
    exist[x1][y1][x2][y2] = true;
    int soma = subrec(x1, y1, x2, y2);
    int area = (x2 - x1 + 1) * (y2 - y1 + 1);
    if (soma == area) {
        return resp[x1][y1][x2][y2] = 1;
    }
    if (!soma) {
        return 0;
    }
    int best = 1000000;
    for (int i = x1; i != x2; ++i) {
        best = std::min(best, dp(x1, y1, i, y2) + dp(i + 1, y1, x2, y2));
    }
    for (int i = y1; i != y2; ++i) {
        best = std::min(best, dp(x1, y1, x2, i) + dp(x1, i + 1, x2, y2));
    }
    return resp[x1][y1][x2][y2] = best;
}

void backtracking(int x1, int y1, int x2, int y2) {
    int soma = subrec(x1, y1, x2, y2);
    int area = (x2 - x1 + 1) * (y2 - y1 + 1);
    if (soma == area) {
        std::cout << x1 << " " << y1 << " " << x2 << " " << y2 << "\n";
        return;
    }
    if (!soma) {
        return;
    }
    int best = 1000000;
    int obj = resp[x1][y1][x2][y2];
    for (int i = x1; i != x2; ++i) {
        int ans = dp(x1, y1, i, y2) + dp(i + 1, y1, x2, y2);
        if (ans == obj) {
            backtracking(x1, y1, i, y2);
            backtracking(i + 1, y1, x2, y2);
            return;
        }
    }
    for (int i = y1; i != y2; ++i) {
        int ans = dp(x1, y1, x2, i) + dp(x1, i + 1, x2, y2);
        if (ans == obj) {
            backtracking(x1, y1, x2, i);
            backtracking(x1, i + 1, x2, y2);
            return;
        }
    }
}

int main() {
    M = 32;
    N = 32;
    
    for (int i = 0; i < N; ++i) {
        for (int j = 0; j < M; ++j) {
            int value;
            std::cin >> value;
            tab[i][j] = value;
        }
    }

    for (int i = 0; i < N; ++i) {
        int val = 0;
        for (int j = 0; j < M; ++j) {
            val += tab[i][j];
            sumed[i][j] = val;
            if (i) sumed[i][j] += sumed[i - 1][j];
        }
    }
    
    dp(0, 0, N - 1, M - 1);
    backtracking(0, 0, N - 1, M - 1);

    return 0;
}