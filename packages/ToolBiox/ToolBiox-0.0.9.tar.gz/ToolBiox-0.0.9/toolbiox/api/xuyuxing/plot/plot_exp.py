data = {'a': np.arange(50),
        'c': np.random.randint(0, 50, 50),
        'd': np.random.randn(50)}

data['b'] = data['a'] + 10 * np.random.randn(50)
data['d'] = np.abs(data['d']) * 100

plt.scatter('a', 'b', c='c', s='d', data=data)

# 这里data读入了一个字典数据，这个时候其它参数就可以通过keys来访问这些数据

plt.xlabel('entry a')
plt.ylabel('entry b')
plt.show()
