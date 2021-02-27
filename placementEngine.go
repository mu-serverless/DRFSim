package main

import (
	"fmt"
	"math"
	"time"
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
	functionName string
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
	return MaxFloatSlice(nodeScore)
}

func maxMinCalculation(fairnessDataList []FairnessData, clusterCPUAvailable float64, clusterMemAvailable float64) ([]float64, []float64) {
	remainingFunctions := len(fairnessDataList)
	for i, _ := range fairnessDataList { // set the desiredCPU, desiredMem, and remainingPodCount
		fairnessDataList[i].desiredCPU = fairnessDataList[i].podCPUUsage * float64(fairnessDataList[i].desiredPodCountSLO)
		fairnessDataList[i].remainingPodCount = fairnessDataList[i].desiredPodCountSLO
		fairnessDataList[i].allocatedCPUFair = 0
		// fairnessDataList[i].desiredPodCountFair = 0
	}
	remainingCPU := clusterCPUAvailable
	for ; remainingFunctions > 0; {
		// fmt.Printf("remainingCPU = %v\n", remainingCPU)
		// fmt.Printf("remainingFunctions = %v\n", remainingFunctions)
		if remainingCPU < 0.01 {
			break
		}
		time.Sleep(0 * time.Second)
		fairShareCPU := remainingCPU / float64(remainingFunctions)
		for i, _ := range fairnessDataList {
			if fairnessDataList[i].desiredCPU - fairnessDataList[i].allocatedCPUFair > 0 && fairnessDataList[i].remainingPodCount > 0 { // Need CPU
				if fairnessDataList[i].desiredCPU - fairnessDataList[i].allocatedCPUFair <= fairShareCPU {
					fairnessDataList[i].remainingPodCount = 0
					remainingCPU -= (fairnessDataList[i].desiredCPU - fairnessDataList[i].allocatedCPUFair)
					fairnessDataList[i].allocatedCPUFair += (fairnessDataList[i].desiredCPU - fairnessDataList[i].allocatedCPUFair)
					remainingFunctions --
					// fmt.Printf("func-%d: ", i)
				} else {
					fairnessDataList[i].allocatedCPUFair += fairShareCPU
					remainingCPU -= fairShareCPU
				}
			}
			// fmt.Printf("func-%d: allocatedCPU: %f\tremainingCPU = %v\n", i, fairnessDataList[i].allocatedCPUFair, remainingCPU)
		}
	}

	remainingFunctions = len(fairnessDataList)
	for i, _ := range fairnessDataList { // set the desiredCPU, desiredMem, and remainingPodCount
		fairnessDataList[i].desiredMem = fairnessDataList[i].podMemUsage * float64(fairnessDataList[i].desiredPodCountSLO)
		fairnessDataList[i].remainingPodCount = fairnessDataList[i].desiredPodCountSLO
		fairnessDataList[i].allocatedMemFair = 0
		// fairnessDataList[i].desiredPodCountFair = 0
	}
	remainingMem := clusterMemAvailable
	for ; remainingFunctions > 0; {
		// fmt.Printf("remainingMem = %v\n", remainingMem)
		// fmt.Printf("remainingFunctions = %v\n", remainingFunctions)
		if remainingMem < 0.01 {
			break
		}
		// time.Sleep(0 * time.Second)
		fairShareMem := remainingMem / float64(remainingFunctions)
		for i, _ := range fairnessDataList {
			if fairnessDataList[i].desiredMem - fairnessDataList[i].allocatedMemFair > 0 && fairnessDataList[i].remainingPodCount > 0 { // Need CPU
				if fairnessDataList[i].desiredMem - fairnessDataList[i].allocatedMemFair <= fairShareMem {
					fairnessDataList[i].remainingPodCount = 0
					remainingMem -= (fairnessDataList[i].desiredMem - fairnessDataList[i].allocatedMemFair)
					fairnessDataList[i].allocatedMemFair += (fairnessDataList[i].desiredMem - fairnessDataList[i].allocatedMemFair)
					remainingFunctions --
					// fmt.Printf("func-%d: ", i)
				} else {
					fairnessDataList[i].allocatedMemFair += fairShareMem
					remainingMem -= fairShareMem
				}
			}
			// fmt.Printf("func-%d: allocatedCPU: %f\tremainingMem = %v\n", i, fairnessDataList[i].allocatedMemFair, remainingMem)
		}
	}

	maxMinCPUValue := make([]float64, 0)
	maxMinMemValue := make([]float64, 0)
	for i, _ := range fairnessDataList {
		maxMinCPUValue = append(maxMinCPUValue, fairnessDataList[i].allocatedCPUFair)
		maxMinMemValue = append(maxMinMemValue, fairnessDataList[i].allocatedMemFair)
	}
	return maxMinCPUValue, maxMinMemValue
}

func fairnessPlacement(fairnessDataList []FairnessData, availableReourcePerNode []ResourceCapacity, clusterCPU float64, clusterMem float64) ([]FairnessData) {
	remainingReourcePerNode := make([]ResourceCapacity, len(availableReourcePerNode))
	for i, _ := range availableReourcePerNode { // init the remainingReourcePerNode
		remainingReourcePerNode[i].CPUCapacity = availableReourcePerNode[i].CPUCapacity
		remainingReourcePerNode[i].MemCapacity = availableReourcePerNode[i].MemCapacity
	}
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
		for i, _ := range fairnessDataList {
			if fairnessDataList[i].remainingPodCount > 0 {
				CPUShare := fairnessDataList[i].allocatedCPUFair / clusterCPU
				MemShare := fairnessDataList[i].allocatedMemFair / clusterMem
				domainShare[i] = math.Max(CPUShare, MemShare)
			} else {
				domainShare[i] = math.Inf(1)
			}
		}
		minDominantShareVal, _ := MinFloatSlice(domainShare) // Find the min dominant share value
		totalDemand := make([]float64, num)
		for i, _ := range domainShare {
			if minDominantShareVal == domainShare[i] {
				totalDemand[i] = fairnessDataList[i].desiredCPU + fairnessDataList[i].desiredMem
			} else {
				totalDemand[i] = math.Inf(1)
			}
		}
		_, funcIndex := MinFloatSlice(totalDemand)
		nodeScore, nodeIndex := scoreWorstFit(funcIndex, fairnessDataList, availableReourcePerNode, remainingReourcePerNode)
		if nodeScore == -1 {
			fairnessDataList[funcIndex].remainingPodCount = 0
			placementCompleted++
			continue
		}
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
	for i, _ := range fairnessDataList { // set the desiredPodCountFair
		fairnessDataList[i].desiredPodCountFair = int32(math.Ceil(fairnessDataList[i].allocatedCPUFair / fairnessDataList[i].podCPUUsage))
	}
	return fairnessDataList
}

func main() {
	/* Simulation Configuration-3:
	 * 2 Nodes: 
	 *			Node-1: <25 CPU, 10 MEM>
	 *			Node-2: <10 CPU, 25 MEM>
	 * 4 Funcs:
	 *			Func-1: 6 Pods, <5, 1> per Pod
	 *			Func-2: 5 Pods, <1, 5> per Pod
	 *			Func-3: 5 Pods, <5, 1> per Pod
	 *			Func-4: 2 Pods, <1, 1> per Pod
	 */
	var clusterCPUAvailable float64 = 35
	var clusterMemAvailable float64 = 35
	fairnessData_1 := FairnessData{ // Func-1
		desiredPodCountSLO: 6, // int32
		// desiredPodCountFair: 0, // int32
		podCPUUsage: 5.0, // float64 // resource usage per pod
		// desiredCPU: 0.0, // float64 // desired resource of this function
		allocatedCPUFair: 0.0, // float64 // fairly allocated resource of this function
		podMemUsage: 1.0, // float64
		// desiredMem: 0.0, // float64
		allocatedMemFair: 0.0, // float64
		// placementDecision []int
		functionName: "fairnessData_1",
	}
	fairnessData_2 := FairnessData{ // Func-2
		desiredPodCountSLO: 5, // int32
		// desiredPodCountFair: 0, // int32
		podCPUUsage: 1.0, // float64 // resource usage per pod
		// desiredCPU: 0.0, // float64 // desired resource of this function
		allocatedCPUFair: 0.0, // float64 // fairly allocated resource of this function
		podMemUsage: 5.0, // float64
		// desiredMem: 0.0, // float64
		allocatedMemFair: 0.0, // float64
		// placementDecision []int
		functionName: "fairnessData_2",
	}
	fairnessData_3 := FairnessData{ // Func-3
		desiredPodCountSLO: 5, // int32
		// desiredPodCountFair: 0, // int32
		podCPUUsage: 5.0, // float64 // resource usage per pod
		// desiredCPU: 0.0, // float64 // desired resource of this function
		allocatedCPUFair: 0.0, // float64 // fairly allocated resource of this function
		podMemUsage: 1.0, // float64
		// desiredMem: 0.0, // float64
		allocatedMemFair: 0.0, // float64
		// placementDecision []int
		functionName: "fairnessData_3",
	}
	fairnessData_4 := FairnessData{ // Func-4
		desiredPodCountSLO: 2, // int32
		// desiredPodCountFair: 0, // int32
		podCPUUsage: 1.0, // float64 // resource usage per pod
		// desiredCPU: 0.0, // float64 // desired resource of this function
		allocatedCPUFair: 0.0, // float64 // fairly allocated resource of this function
		podMemUsage: 1.0, // float64
		// desiredMem: 0.0, // float64
		allocatedMemFair: 0.0, // float64
		// placementDecision []int
		functionName: "fairnessData_4",
	}

	// Collect over time
	cpuShare := make([]float64, 0)
	cpuShareList := [][]float64{cpuShare, cpuShare, cpuShare, cpuShare}
	memShare := make([]float64, 0)
	memShareList := [][]float64{memShare, memShare, memShare, memShare}
	maxMinCPUShare := make([]float64, 0)
	maxMinCPUShareList := [][]float64{maxMinCPUShare, maxMinCPUShare, maxMinCPUShare, maxMinCPUShare}
	maxMinMemShare := make([]float64, 0)
	maxMinMemShareList := [][]float64{maxMinMemShare, maxMinMemShare, maxMinMemShare, maxMinMemShare}
	for clk := 0; clk < 30; clk++ {
		fairnessDataList := make([]FairnessData, 0)
		fairnessDataList_1 := make([]FairnessData, 0)
		availableReourcePerNode := []ResourceCapacity{
			ResourceCapacity{
				25,
				10,
			},
			ResourceCapacity{
				10,
				25,
			},
		}
		// DRF
		if clk >= 0 && clk < 3 {
			fairnessDataList = []FairnessData{fairnessData_1, fairnessData_4}
		} else if clk >= 3 && clk < 5 {
			fairnessDataList = []FairnessData{fairnessData_1, fairnessData_2, fairnessData_4}
		} else if clk >= 5 && clk < 10 {
			fairnessDataList = []FairnessData{fairnessData_1, fairnessData_2, fairnessData_3, fairnessData_4}
		} else if clk >= 10 && clk < 20 {
			fairnessDataList = []FairnessData{fairnessData_1, fairnessData_3, fairnessData_4}
		} else if clk >= 20 && clk < 25 {
			fairnessDataList = []FairnessData{fairnessData_1, fairnessData_2, fairnessData_3, fairnessData_4}
		} else {
			fairnessDataList = []FairnessData{fairnessData_1, fairnessData_2, fairnessData_4}
		}
		// Max-min
		if clk >= 0 && clk < 3 {
			fairnessDataList_1 = []FairnessData{fairnessData_1, fairnessData_4}
		} else if clk >= 3 && clk < 5 {
			fairnessDataList_1 = []FairnessData{fairnessData_1, fairnessData_2, fairnessData_4}
		} else if clk >= 5 && clk < 10 {
			fairnessDataList_1 = []FairnessData{fairnessData_1, fairnessData_2, fairnessData_3, fairnessData_4}
		} else if clk >= 10 && clk < 20 {
			fairnessDataList_1 = []FairnessData{fairnessData_1, fairnessData_3, fairnessData_4}
		} else if clk >= 20 && clk < 25 {
			fairnessDataList_1 = []FairnessData{fairnessData_1, fairnessData_2, fairnessData_3, fairnessData_4}
		} else {
			fairnessDataList_1 = []FairnessData{fairnessData_1, fairnessData_2, fairnessData_4}
		}
		output := fairnessPlacement(fairnessDataList, availableReourcePerNode, clusterCPUAvailable, clusterMemAvailable)
		if clk == 0 { //5 && clk <= 7 {
			fmt.Printf("* * * * * * * * * * * * * * * * clk = %v * * * * * * * * * * * * * * * * * * * * \n", clk)
			fmt.Printf("output = %v\n\n", output)
			fmt.Printf("availableReourcePerNode = %v\n\n", availableReourcePerNode)
		}
		// fmt.Printf("* * * * * * * * * * * * * * * * clk = %v * * * * * * * * * * * * * * * * * * * * \n", clk)
		maxMinCPUShareVal, maxMinMemShareVal := maxMinCalculation(fairnessDataList_1, clusterCPUAvailable, clusterMemAvailable)

		// Write results
		if clk >= 0 && clk < 3 {
			// fairnessDataList = []FairnessData{fairnessData_1, fairnessData_4}
			cpuShareList[0] = append(cpuShareList[0], output[0].allocatedCPUFair)
			cpuShareList[1] = append(cpuShareList[1], 0)
			cpuShareList[2] = append(cpuShareList[2], 0)
			cpuShareList[3] = append(cpuShareList[3], output[1].allocatedCPUFair)

			memShareList[0] = append(memShareList[0], output[0].allocatedMemFair)
			memShareList[1] = append(memShareList[1], 0)
			memShareList[2] = append(memShareList[2], 0)
			memShareList[3] = append(memShareList[3], output[1].allocatedMemFair)

			maxMinCPUShareList[0] = append(maxMinCPUShareList[0], maxMinCPUShareVal[0])
			maxMinCPUShareList[1] = append(maxMinCPUShareList[1], 0)
			maxMinCPUShareList[2] = append(maxMinCPUShareList[2], 0)
			maxMinCPUShareList[3] = append(maxMinCPUShareList[3], maxMinCPUShareVal[1])

			maxMinMemShareList[0] = append(maxMinMemShareList[0], maxMinMemShareVal[0])
			maxMinMemShareList[1] = append(maxMinMemShareList[1], 0)
			maxMinMemShareList[2] = append(maxMinMemShareList[2], 0)
			maxMinMemShareList[3] = append(maxMinMemShareList[3], maxMinMemShareVal[1])
		} else if clk >= 3 && clk < 5 {
			// fairnessDataList = []FairnessData{fairnessData_1, fairnessData_2, fairnessData_4}
			cpuShareList[0] = append(cpuShareList[0], output[0].allocatedCPUFair)
			cpuShareList[1] = append(cpuShareList[1], output[1].allocatedCPUFair)
			cpuShareList[2] = append(cpuShareList[2], 0)
			cpuShareList[3] = append(cpuShareList[3], output[2].allocatedCPUFair)

			memShareList[0] = append(memShareList[0], output[0].allocatedMemFair)
			memShareList[1] = append(memShareList[1], output[1].allocatedMemFair)
			memShareList[2] = append(memShareList[2], 0)
			memShareList[3] = append(memShareList[3], output[2].allocatedMemFair)

			maxMinCPUShareList[0] = append(maxMinCPUShareList[0], maxMinCPUShareVal[0])
			maxMinCPUShareList[1] = append(maxMinCPUShareList[1], maxMinCPUShareVal[1])
			maxMinCPUShareList[2] = append(maxMinCPUShareList[2], 0)
			maxMinCPUShareList[3] = append(maxMinCPUShareList[3], maxMinCPUShareVal[2])

			maxMinMemShareList[0] = append(maxMinMemShareList[0], maxMinMemShareVal[0])
			maxMinMemShareList[1] = append(maxMinMemShareList[1], maxMinMemShareVal[1])
			maxMinMemShareList[2] = append(maxMinMemShareList[2], 0)
			maxMinMemShareList[3] = append(maxMinMemShareList[3], maxMinMemShareVal[2])
		} else if clk >= 5 && clk < 10 {
			// fairnessDataList = []FairnessData{fairnessData_1, fairnessData_2, fairnessData_3, fairnessData_4}
			cpuShareList[0] = append(cpuShareList[0], output[0].allocatedCPUFair)
			cpuShareList[1] = append(cpuShareList[1], output[1].allocatedCPUFair)
			cpuShareList[2] = append(cpuShareList[2], output[2].allocatedCPUFair)
			cpuShareList[3] = append(cpuShareList[3], output[3].allocatedCPUFair)

			memShareList[0] = append(memShareList[0], output[0].allocatedMemFair)
			memShareList[1] = append(memShareList[1], output[1].allocatedMemFair)
			memShareList[2] = append(memShareList[2], output[2].allocatedMemFair)
			memShareList[3] = append(memShareList[3], output[3].allocatedMemFair)

			maxMinCPUShareList[0] = append(maxMinCPUShareList[0], maxMinCPUShareVal[0])
			maxMinCPUShareList[1] = append(maxMinCPUShareList[1], maxMinCPUShareVal[1])
			maxMinCPUShareList[2] = append(maxMinCPUShareList[2], maxMinCPUShareVal[2])
			maxMinCPUShareList[3] = append(maxMinCPUShareList[3], maxMinCPUShareVal[3])

			maxMinMemShareList[0] = append(maxMinMemShareList[0], maxMinMemShareVal[0])
			maxMinMemShareList[1] = append(maxMinMemShareList[1], maxMinMemShareVal[1])
			maxMinMemShareList[2] = append(maxMinMemShareList[2], maxMinMemShareVal[2])
			maxMinMemShareList[3] = append(maxMinMemShareList[3], maxMinMemShareVal[3])
		} else if clk >= 10 && clk < 20 {
			// fairnessDataList = []FairnessData{fairnessData_1, fairnessData_3, fairnessData_4}
			cpuShareList[0] = append(cpuShareList[0], output[0].allocatedCPUFair)
			cpuShareList[1] = append(cpuShareList[1], 0)
			cpuShareList[2] = append(cpuShareList[2], output[1].allocatedCPUFair)
			cpuShareList[3] = append(cpuShareList[3], output[2].allocatedCPUFair)

			memShareList[0] = append(memShareList[0], output[0].allocatedMemFair)
			memShareList[1] = append(memShareList[1], 0)
			memShareList[2] = append(memShareList[2], output[1].allocatedMemFair)
			memShareList[3] = append(memShareList[3], output[2].allocatedMemFair)

			maxMinCPUShareList[0] = append(maxMinCPUShareList[0], maxMinCPUShareVal[0])
			maxMinCPUShareList[1] = append(maxMinCPUShareList[1], 0)
			maxMinCPUShareList[2] = append(maxMinCPUShareList[2], maxMinCPUShareVal[1])
			maxMinCPUShareList[3] = append(maxMinCPUShareList[3], maxMinCPUShareVal[2])

			maxMinMemShareList[0] = append(maxMinMemShareList[0], maxMinMemShareVal[0])
			maxMinMemShareList[1] = append(maxMinMemShareList[1], 0)
			maxMinMemShareList[2] = append(maxMinMemShareList[2], maxMinMemShareVal[1])
			maxMinMemShareList[3] = append(maxMinMemShareList[3], maxMinMemShareVal[2])
		} else if clk >= 20 && clk < 25 {
			// fairnessDataList = []FairnessData{fairnessData_1, fairnessData_2, fairnessData_3, fairnessData_4}
			cpuShareList[0] = append(cpuShareList[0], output[0].allocatedCPUFair)
			cpuShareList[1] = append(cpuShareList[1], output[1].allocatedCPUFair)
			cpuShareList[2] = append(cpuShareList[2], output[2].allocatedCPUFair)
			cpuShareList[3] = append(cpuShareList[3], output[3].allocatedCPUFair)

			memShareList[0] = append(memShareList[0], output[0].allocatedMemFair)
			memShareList[1] = append(memShareList[1], output[1].allocatedMemFair)
			memShareList[2] = append(memShareList[2], output[2].allocatedMemFair)
			memShareList[3] = append(memShareList[3], output[3].allocatedMemFair)

			maxMinCPUShareList[0] = append(maxMinCPUShareList[0], maxMinCPUShareVal[0])
			maxMinCPUShareList[1] = append(maxMinCPUShareList[1], maxMinCPUShareVal[1])
			maxMinCPUShareList[2] = append(maxMinCPUShareList[2], maxMinCPUShareVal[2])
			maxMinCPUShareList[3] = append(maxMinCPUShareList[3], maxMinCPUShareVal[3])

			maxMinMemShareList[0] = append(maxMinMemShareList[0], maxMinMemShareVal[0])
			maxMinMemShareList[1] = append(maxMinMemShareList[1], maxMinMemShareVal[1])
			maxMinMemShareList[2] = append(maxMinMemShareList[2], maxMinMemShareVal[2])
			maxMinMemShareList[3] = append(maxMinMemShareList[3], maxMinMemShareVal[3])
		} else {
			// fairnessDataList = []FairnessData{fairnessData_1, fairnessData_2, fairnessData_4}
			cpuShareList[0] = append(cpuShareList[0], output[0].allocatedCPUFair)
			cpuShareList[1] = append(cpuShareList[1], output[1].allocatedCPUFair)
			cpuShareList[2] = append(cpuShareList[2], 0)
			cpuShareList[3] = append(cpuShareList[3], output[2].allocatedCPUFair)

			memShareList[0] = append(memShareList[0], output[0].allocatedMemFair)
			memShareList[1] = append(memShareList[1], output[1].allocatedMemFair)
			memShareList[2] = append(memShareList[2], 0)
			memShareList[3] = append(memShareList[3], output[2].allocatedMemFair)

			maxMinCPUShareList[0] = append(maxMinCPUShareList[0], maxMinCPUShareVal[0])
			maxMinCPUShareList[1] = append(maxMinCPUShareList[1], maxMinCPUShareVal[1])
			maxMinCPUShareList[2] = append(maxMinCPUShareList[2], 0)
			maxMinCPUShareList[3] = append(maxMinCPUShareList[3], maxMinCPUShareVal[2])

			maxMinMemShareList[0] = append(maxMinMemShareList[0], maxMinMemShareVal[0])
			maxMinMemShareList[1] = append(maxMinMemShareList[1], maxMinMemShareVal[1])
			maxMinMemShareList[2] = append(maxMinMemShareList[2], 0)
			maxMinMemShareList[3] = append(maxMinMemShareList[3], maxMinMemShareVal[2])
		}
		// fmt.Printf("availableReourcePerNode = %v\n", availableReourcePerNode)
	}
	fmt.Printf("cpuShareList = %v\n", cpuShareList)
	fmt.Printf("maxMinCPUShareList = %v\n\n", maxMinCPUShareList)

	fmt.Printf("memShareList = %v\n", memShareList)
	fmt.Printf("maxMinMemShareList = %v\n", maxMinMemShareList)
}