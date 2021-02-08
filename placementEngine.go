package main

import (
	"fmt"
	"math"
	// "time"
)

type FairnessData struct {
	// metricKey types.NamespacedName
	// runner *scalerRunner
	// desiredPodCount int32
	desiredPodCountSLO int32
	desiredPodCountFair int32
	podCPUUsage float64 // resource usage per pod
	desiredCPU float64 // desired resource of this function
	allocatedCPUFair float64 // fairly allocated resource of this function
	podMemUsage float64
	desiredMem float64
	allocatedMemFair float64
	placementDecision []int
	remainingPodCount int32
	// functionName string
}

type ResourceCapacity struct {
	CPUCapacity float64
	MemCapacity float64
}

func MinFloatSlice(input []float64) (float64, int) {
	var min float64 = input[0]
	var index int = 0
    for i, value := range input {
        if min > value {
			min = value
			index = i
        }
    }
    return min, index
}

func MaxFloatSlice(input []float64) (float64, int) {
	var max float64 = input[0]
	var index int = 0
    for i, value := range input {
        if max < value {
			max = value
			index = i
        }
    }
    return max, index
}

func scoreWorstFit(fIndex int, fairnessDataList []FairnessData, availableReourcePerNode []ResourceCapacity, remainingReourcePerNode []ResourceCapacity) (float64, int) {
	num := len(availableReourcePerNode)
	nodeScore := make([]float64, num)
	// fmt.Printf("In scoreWorstFit, remainingReourcePerNode = %v\n", remainingReourcePerNode)
	for i, _ := range availableReourcePerNode {
		if remainingReourcePerNode[i].CPUCapacity > 0 && remainingReourcePerNode[i].MemCapacity > 0 { 
			if remainingReourcePerNode[i].CPUCapacity >= fairnessDataList[fIndex].podCPUUsage && remainingReourcePerNode[i].MemCapacity >= fairnessDataList[fIndex].podMemUsage {
				nodeScore[i] = (remainingReourcePerNode[i].CPUCapacity - fairnessDataList[fIndex].podCPUUsage) / float64(availableReourcePerNode[i].CPUCapacity) + (remainingReourcePerNode[i].MemCapacity - fairnessDataList[fIndex].podMemUsage) / float64(availableReourcePerNode[i].MemCapacity)
			} else {
				nodeScore[i] = -1
			}
		} else {
			nodeScore[i] = -1
		}
	}
	// fmt.Printf("In scoreWorstFit, nodeScore = %v\n", nodeScore)
	return MaxFloatSlice(nodeScore)
}

func fairnessPlacement(fairnessDataList []FairnessData, availableReourcePerNode []ResourceCapacity, clusterCPU float64, clusterMem float64) ([]FairnessData) {
	remainingReourcePerNode := availableReourcePerNode
	fmt.Printf("In DRF, remainingReourcePerNode = %v\n", remainingReourcePerNode)
	fmt.Printf("In DRF, availableReourcePerNode = %v\n", availableReourcePerNode)
	fmt.Printf("In DRF, fairnessDataList = %v\n", fairnessDataList)
	for i, _ := range fairnessDataList { // set the desiredCPU, desiredMem, and remainingPodCount
		fairnessDataList[i].desiredCPU = fairnessDataList[i].podCPUUsage * float64(fairnessDataList[i].desiredPodCountSLO)
		fairnessDataList[i].desiredMem = fairnessDataList[i].podMemUsage * float64(fairnessDataList[i].desiredPodCountSLO)
		fairnessDataList[i].remainingPodCount = fairnessDataList[i].desiredPodCountSLO
	}
	num := len(fairnessDataList) // Number of Functions
	var placementCompleted int = 0
	for { // max-min allocation
		if placementCompleted == num {
			break
		}
		domainShare := make([]float64, num)
		fmt.Printf("[For-loop] remainingReourcePerNode = %v\n", remainingReourcePerNode)
		// fmt.Printf("[For-loop] availableReourcePerNode = %v\n", availableReourcePerNode)
		for i, _ := range fairnessDataList {
			if fairnessDataList[i].remainingPodCount > 0 {
				CPUShare := fairnessDataList[i].allocatedCPUFair / clusterCPU
				MemShare := fairnessDataList[i].allocatedMemFair / clusterMem
				domainShare[i] = math.Max(CPUShare, MemShare)
			} else {
				domainShare[i] = math.Inf(1)
			}
			// fmt.Printf("fairnessDataList[%v].allocatedCPUFair = %v\n", i, fairnessDataList[i].allocatedCPUFair)
			// fairnessDataList[i].desiredPodCountFair = 2
		}
		// fmt.Printf("In DRF, domainShare = %v\n", domainShare)
		// time.Sleep(1 * time.Second) 
		_, funcIndex := MinFloatSlice(domainShare)
		fmt.Printf("In DRF, funcIndex = %v\n", funcIndex)
		nodeScore, nodeIndex := scoreWorstFit(funcIndex, fairnessDataList, availableReourcePerNode, remainingReourcePerNode)
		// fmt.Printf("In DRF, nodeScore = %f, nodeIndex = %d\n", nodeScore, nodeIndex)
		if nodeScore == -1 {
			fairnessDataList[funcIndex].remainingPodCount = 0
			placementCompleted++
			continue
		}
		// fmt.Printf("In DRF, placementCompleted = %v\n", placementCompleted)

		fairnessDataList[funcIndex].allocatedCPUFair += fairnessDataList[funcIndex].podCPUUsage
		fairnessDataList[funcIndex].allocatedMemFair += fairnessDataList[funcIndex].podMemUsage
		fairnessDataList[funcIndex].remainingPodCount -= 1 
		fairnessDataList[funcIndex].placementDecision = append(fairnessDataList[funcIndex].placementDecision, nodeIndex)
		if fairnessDataList[funcIndex].remainingPodCount == 0 {
			placementCompleted++
		}

		remainingReourcePerNode[nodeIndex].CPUCapacity -= fairnessDataList[funcIndex].podCPUUsage
		remainingReourcePerNode[nodeIndex].MemCapacity -= fairnessDataList[funcIndex].podMemUsage

	}
	fmt.Printf("[For-loop] remainingReourcePerNode = %v\n", remainingReourcePerNode)
	for i, _ := range fairnessDataList { // set the desiredPodCountFair
		fairnessDataList[i].desiredPodCountFair = int32(math.Ceil(fairnessDataList[i].allocatedCPUFair / fairnessDataList[i].podCPUUsage))
	}
	fmt.Printf("In fairnessAllocation (end), fairnessDataList = %v\n", fairnessDataList)
	return fairnessDataList
}


/* func test() {
	fmt.Printf("Test Func\n")
	// Step-2: Do the DRF && Do the scoring on the node
	// fairnessDataList = fairnessPlacement(fairnessDataList, availableReourcePerNode, clusterCPUAvailable, clusterMemAvailable)

	func MaxFloatSlice() test
	var array1 = []float64{1.1, 2.2, 3.3, 6.4, 5.5}
	max, index := MaxFloatSlice(array1)
	fmt.Printf("%d, %d\n", max, index)

	func MinFloatSlice() test
	var array1 = []float64{1.1, 0.2, 3.3, 6.4, 5.5}
	val, index := MinFloatSlice(array1)
	fmt.Printf("%f, %d\n", val, index)
} */

func main() {
	fmt.Printf("main func\n")
	/* Simulation Configuration-1:
	 * 2 Nodes: 
	 *			Node-1: <25 CPU, 6 MEM>
	 *			Node-2: <6 CPU, 25 MEM>
	 * 3 Funcs:
	 *			Func-1: 5 Pods, <5, 1> per Pod
	 *			Func-2: 5 Pods, <1, 5> per Pod
	 *			Func-3: 1 Pod, <1, 1> per Pod
	 */
	var clusterCPUAvailable float64 = 31
	var clusterMemAvailable float64 = 31
	availableReourcePerNode := []ResourceCapacity{
		ResourceCapacity{
			25,
			6,
		},
		ResourceCapacity{
			6,
			25,
		},
	}
	fairnessDataList := []FairnessData{
		FairnessData{ // Func-1
			desiredPodCountSLO: 5, // int32
			// desiredPodCountFair: 0, // int32
			podCPUUsage: 5.0, // float64 // resource usage per pod
			// desiredCPU: 0.0, // float64 // desired resource of this function
			allocatedCPUFair: 0.0, // float64 // fairly allocated resource of this function
			podMemUsage: 1.0, // float64
			// desiredMem: 0.0, // float64
			allocatedMemFair: 0.0, // float64
			// placementDecision []int
		},
		FairnessData{ // Func-2
			desiredPodCountSLO: 5, // int32
			// desiredPodCountFair: 0, // int32
			podCPUUsage: 1.0, // float64 // resource usage per pod
			// desiredCPU: 0.0, // float64 // desired resource of this function
			allocatedCPUFair: 0.0, // float64 // fairly allocated resource of this function
			podMemUsage: 5.0, // float64
			// desiredMem: 0.0, // float64
			allocatedMemFair: 0.0, // float64
			// placementDecision []int
		},
		FairnessData{ // Func-3
			desiredPodCountSLO: 1, // int32
			// desiredPodCountFair: 0, // int32
			podCPUUsage: 1.0, // float64 // resource usage per pod
			// desiredCPU: 0.0, // float64 // desired resource of this function
			allocatedCPUFair: 0.0, // float64 // fairly allocated resource of this function
			podMemUsage: 1.0, // float64
			// desiredMem: 0.0, // float64
			allocatedMemFair: 0.0, // float64
			// placementDecision []int
		},
	}
	fairnessDataList = fairnessPlacement(fairnessDataList, availableReourcePerNode, clusterCPUAvailable, clusterMemAvailable)
}