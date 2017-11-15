#include<bits/stdc++.h>

using namespace std;

typedef long long int lli;

lli Y,A,B;

int main(){
	lli T;
	cin >> T;
	while(T--){
		string A;	
		cin >> A;
		lli prev=0,n=A.size(),sz,ans=0;
		for(lli next=1;next<n;next++){
			if(A[next]==A[prev]){
				continue;
			}
			else{
				sz = next - prev;
				if(sz!=1){
					ans+=sz*(sz-1)/2;
					if(prev-1>=0){
						if(A[prev-1]==A[next])
							ans+=1;
					}
				}
				else{
					if(prev-1>=0){
						if(A[prev-1]==A[next])
							ans+=1;
					}	
				}
				prev = next;
			}
		}
		
		sz = n-prev;
		if(sz!=1){
					ans+=sz*(sz-1)/2;
					
				}		

		cout << ans <<endl;
	}

	return 0;
}