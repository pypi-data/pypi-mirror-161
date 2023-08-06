def profit(prices, k):
    ilow = []
    ihigh = []
    vlow = []
    vhigh = []
    sortedLowDict = {}
    sortedHighDict = {}
    low = prices.copy()
    high = prices.copy()
    kt = 0
    kth = 0
    buy = 0
    sell = 0
    totalk = 0
    totlalProfit = 0

    while kt != k:
        m = min(low)
        # print("m : ", m)
        im = prices.index(m)
        ilow.append(im)
        low.remove(m)
        vlow.append(m)

        h = max(high)
        ih = prices.index(h)
        ihigh.append(ih)
        high.remove(h)
        vhigh.append(h)
        kt += 1

    # print("vlow : ", vlow)

    lowDict = dict(zip(ilow, vlow))
    print("lowDict : ", lowDict)
    highDict = dict(zip(ihigh, vhigh))
    print("highDict : ", highDict)

    for elem in sorted(lowDict.items()):
        sortedLowDict.update({elem[0]: elem[1]})
    print("sortedLowDict : ", sortedLowDict)
    for elem in sorted((highDict.items())):
        sortedHighDict.update({elem[0]: elem[1]})
    print("sortedHighDict : ", sortedHighDict)

    while kth != k:
        minVal = list(sortedLowDict.values())[kth]
        maxVal = list(sortedHighDict.values())[kth]
        hindex = prices.index(h)
        if maxVal is not None:
            if hindex < minVal and hindex > maxVal:



    while k != totalk:
        mkey = list(sortedLowDict.keys())[totalk]
        # print("mkey : ", mkey)
        hkey = list(sortedHighDict.keys())[totalk]
        # print("hkey : ", hkey)
        vm = sortedLowDict.get(mkey)
        vh = sortedHighDict.get(hkey)

        for n in prices:
            if n == vm:
                buy += n
                print("buy : ", n)
            elif n == vh:
                sell += n
                print("sell : ", n)

        totalk += 1

    totlalProfit = sell - buy


    return totlalProfit

#Driver Code
# ui = input("enter prices\n")
ui = [3, 2, 6, 5, 0, 3]
print(ui)
k = 2
print(profit(ui, k))