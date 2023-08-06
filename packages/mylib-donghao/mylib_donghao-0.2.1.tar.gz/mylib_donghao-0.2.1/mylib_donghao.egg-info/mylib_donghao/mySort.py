##快速排序
def quickSort(arr, I, left=None, right=None):
    left = 0 if not isinstance(left, (int, float)) else left
    right = len(arr)-1 if not isinstance(right, (int, float)) else right
    if left < right:
        partitionIndex = partition(arr, I, left, right)
        quickSort(arr, I, left, partitionIndex-1)
        quickSort(arr, I, partitionIndex+1, right)
    return arr, I

def partition(arr, I, left, right):
    pivot = left
    index = pivot+1
    i = index
    while  i <= right:
        if arr[i] < arr[pivot]:
            swap(arr, i, index)
            swap(I, i, index)
            index += 1
        i+=1
    swap(arr, pivot, index-1)
    swap(I, pivot, index-1)
    return index-1

def swap(arr, i, j):
    arr[i], arr[j] = arr[j], arr[i]
