import random

def quicksort(nums, fst, lst):
   if fst >= lst: return 
 
   i, j = fst, lst # начальный и конечный индексы
   pivot = nums[random.randint(fst, lst)] # опорный элемент, относительно которго мы будем сортировать массив
 
   while i <= j: # пока левый индекс меньше правого
       while nums[i] < pivot: i += 1 
       while nums[j] > pivot: j -= 1
       if i <= j:
           nums[i], nums[j] = nums[j], nums[i]
           i, j = i + 1, j - 1
   quicksort(nums, fst, j)
   quicksort(nums, i, lst)


nums = [1, 8, 5, 4, 7, 3]

quicksort(nums, 0, len(nums) - 1)


print(nums)