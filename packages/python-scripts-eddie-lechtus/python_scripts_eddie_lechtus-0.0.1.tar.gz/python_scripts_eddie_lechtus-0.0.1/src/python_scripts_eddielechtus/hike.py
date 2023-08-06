import heapq
from typing import List


class Solution:
    def minimumEffortPath(self, heights: List[List[int]]) -> int:

        M, N = map(len, (heights, heights[0]))
        heap = [(0, 0, 0)]
        seen = set()
        result = 0

        while heap:

            # Pop
            effort, i, j = heapq.heappop(heap)

            # Mark seen
            seen.add((i, j))

            # Update minimum "effort"
            result = max(result, effort)

            # Success condition
            if i == M - 1 and j == N - 1:
                break

            # BFS
            for x, y in [(i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)]:
                if not (x >= 0 <= y): continue
                if x >= M or y >= N: continue
                if (x, y) in seen: continue
                effort = abs(heights[i][j] - heights[x][y])
                heapq.heappush(heap, (effort, x, y))

        return result

obj = Solution()
heights = [[1,2,2],[3,8,2],[5,3,5]]
obj.minimumEffortPath(heights)