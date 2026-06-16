package main

import (
	"fmt"
	"os"
	"os/exec"
	"strings"
	"sync"
	"time"

	"gopkg.in/yaml.v3"
)

// MOSKV-1 APEX KERNEL (Golang Core)
// Reality Level: C5-REAL
// JIT Autopoietic Binary

const (
	LogFile    = "/tmp/moskv_core.log"
	SwarmCount = 1000
)

func logExergy(msg string) {
	f, err := os.OpenFile(LogFile, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err == nil {
		f.WriteString(fmt.Sprintf("[%s] %s\n", time.Now().Format(time.RFC3339), msg))
		f.Close()
	}
	fmt.Println(msg)
}

func notifyOS(title, message string) {
	cmd := fmt.Sprintf(`display notification "%s" with title "%s"`, message, title)
	exec.Command("osascript", "-e", cmd).Run()
}

func runSwarm() {
	logExergy("=== [INIT] GO-NATIVE SWARM ENGAGED ===")
	notifyOS("MOSKV-1 [SWARM]", "1000 Goroutines deployed. Hunting entropy.")

	var wg sync.WaitGroup
	ticker := time.NewTicker(6 * time.Second) // 10 cycles/min
	defer ticker.Stop()

	// Lifespan 4 Hours
	end := time.Now().Add(4 * time.Hour)

	cycle := 1
	for time.Now().Before(end) {
		<-ticker.C
		for i := 0; i < SwarmCount; i++ {
			wg.Add(1)
			go func(id int) {
				defer wg.Done()
				// Agent 42 is the hunter
				if id == 42 {
					out, _ := exec.Command("sh", "-c", "ps -eo pid,pcpu,comm | grep -E 'node|python' | awk '$2 > 50.0 {print $1}'").Output()
					pids := strings.Fields(string(out))
					for _, pid := range pids {
						if pid != "" {
							exec.Command("kill", "-9", pid).Run()
							logExergy(fmt.Sprintf("[KILL] High Entropy PID %s Terminated.", pid))
						}
					}
				}
			}(i)
		}
		wg.Wait()
		if cycle%10 == 0 {
			logExergy(fmt.Sprintf("[HEARTBEAT] Cycle %d | Swarm Synced.", cycle))
		}
		cycle++
	}
	logExergy("=== [HALT] SWARM LIFESPAN DEPLETED ===")
}

// Vibe DSL Structure
type VibeDict struct {
	Vibes []struct {
		ID           string   `yaml:"id"`
		Patterns     []string `yaml:"patterns"`
		Command      string   `yaml:"command"`
		Notification string   `yaml:"notification"`
	} `yaml:"vibes"`
}

func runVibe(input string) {
	data, err := os.ReadFile("vibe_dict.yaml")
	if err != nil {
		logExergy("[FAIL] Missing vibe_dict.yaml")
		os.Exit(1)
	}

	var dict VibeDict
	yaml.Unmarshal(data, &dict)

	input = strings.ToLower(strings.TrimSpace(input))

	for _, vibe := range dict.Vibes {
		for _, pattern := range vibe.Patterns {
			if strings.Contains(input, pattern) {
				logExergy(fmt.Sprintf("[VIBE COMPILED] %s -> %s", pattern, vibe.Command))
				notifyOS("MOSKV-1 [VIBE EXEC]", vibe.Notification)
				exec.Command("sh", "-c", vibe.Command).Run()
				return
			}
		}
	}
	logExergy("[FAIL] Unknown Vibe. Dropping.")
	os.Exit(127) // Return to ZSH
}

func main() {
	if len(os.Args) < 2 {
		fmt.Println("Usage: ./moskv-core <vector>")
		os.Exit(1)
	}

	vector := os.Args[1]

	switch vector {
	case "swarm":
		// Daemonize self if not background
		if len(os.Args) == 2 {
			cmd := exec.Command("nohup", os.Args[0], "swarm", "--daemon")
			cmd.Start()
			fmt.Println("Swarm daemonized. Check", LogFile)
			os.Exit(0)
		}
		runSwarm()
	case "sleep":
		logExergy("Initiating Sleep Protocol...")
		exec.Command("sh", "-c", "tar -czf SOTA_Archive/sota_snapshot.tar.gz . && purge && pmset sleepnow").Run()
	case "vibe":
		if len(os.Args) > 2 {
			runVibe(strings.Join(os.Args[2:], " "))
		}
	default:
		os.Exit(127)
	}
}
