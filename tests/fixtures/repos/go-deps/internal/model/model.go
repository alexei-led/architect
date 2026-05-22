// Package model should be a leaf of pure types, but it imports store,
// inverting the intended handler -> store -> model direction.
package model

import "example.com/go-deps/internal/store"

type Order struct {
	ID    string
	Total int
}

// Save leaks persistence into the model layer (inverted dependency).
func (o Order) Save() error {
	return store.Put(o.ID, o.Total)
}
