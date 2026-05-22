// Package handler is the intended top layer.
package handler

import "example.com/go-deps/internal/model"

func Place(id string, total int) error {
	o := model.Order{ID: id, Total: total}
	return o.Save()
}
