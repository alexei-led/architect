// Package store is the hub: persistence used everywhere. Pure leaf, no smell
// here on its own.
package store

var data = map[string]int{}

func Put(id string, total int) error {
	data[id] = total
	return nil
}

func Get(id string) (int, bool) {
	v, ok := data[id]
	return v, ok
}
