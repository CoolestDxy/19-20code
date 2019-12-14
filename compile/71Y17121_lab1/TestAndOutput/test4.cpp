#include<iostream>
#include<cstdlib>
#include<ctime>
//随便找了一个数据结构的代码
using namespace std;
int main()
{
	srand((unsigned)time(NULL));
	int a[7] = {};
	int i=0;
	while(i<7)
	{
		int t = rand() % 8;
		bool f = 0;
		for (int j = 0; j <= i; j++)
		{
			if (a[j] == t)f = 1;
		}
		if (f == 0)
		{
			a[i] = t;
			i++;
			cout << t << endl;
		}
	}
	system("pause");
	return 0;
}