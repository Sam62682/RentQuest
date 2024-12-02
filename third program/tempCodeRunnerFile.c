#include<stio.h>
main(){
    int arr1[3][3] = {{1,2, 3},{4,5,6},{7,8,9}};
    int arr2[][] = {{9,8,7},{6,5,4},{3,2,1}};
    int i = 0,j=0;
    int result[3][3];

    for(;i<3;i++){
        for(j=0;j<3;j++){
            result[i][j] = arr1[i][j] + arr2[i][j];
            printf("%d ",result[i][j]);
        }
        printf("\n");

        
}
}