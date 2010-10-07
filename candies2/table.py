#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gobject
import clutter
from box import AlignedElement

class TableCellAligner(AlignedElement):
    __gtype_name__ = 'TableCellAligner'
    
    def __init__(self, **args):
        AlignedElement.__init__(self, **args)

class Table(clutter.Actor, clutter.Container):
    __gtype_name__ = 'Table'
    """
    A table layout
    """
    def __init__(self, rows=0, columns=0, margin=0, padding=0, spacing=0, pick_enabled=True):
        clutter.Actor.__init__(self)
        self.pick_enabled = pick_enabled
        self.margin = margin
        self.padding = padding
        self.spacing = spacing
        
        if isinstance(rows, int):
            self._rows = ['auto' for i in range(rows)]
        elif isinstance(rows, list):
            self._rows = rows
        else:
            raise TypeError('Columns type and must be int or list')
        if isinstance(columns, int):
            self._columns = ['auto' for i in range(columns)]
        elif isinstance(columns, list):
            self._columns = columns
        else:
            raise TypeError('Columns type and must be int or list')
        self._size = len(self._columns) * len(self._rows)
        self._matrix = [[None for i in range(len(self._columns))] for i in range(len(self._rows))]
    
    def add(self, actor, column=-1, row=-1, alignment='center', expand=False, keep_ratio=False):
        if actor.get_parent() != self:
            place = (None, None)
            if column == -1 and row == -1:
                added = False
                for r in range(len(self._rows)):
                    for c in range(len(self._columns)):
                        if self._matrix[r][c] is None:
                            place = (r, c)
                            added = True
                            break
                    if added:
                        break
                if not added:
                    # No place in table
                    raise Exception('No remaining place in table %s to add actor %s' %(self, actor))
            elif row != -1:
                if row < self._rows:
                    if column == -1:
                        for c in range(len(self._columns)):
                            if self._matrix[row][c] is None:
                                column = c
                                break
                    if column == -1:
                        raise Exception('No remaining place in row %s of table %s to add actor %s' %(row, self, actor))
                    place = (row, column)
                else:
                    raise IndexError('Can not add actor %s in row %s in table %s, table has only %s rows' %(actor, row, self, actor, self._rows))
            elif column != -1:
                if column < self._columns:
                    if row == -1:
                        for r in range(len(self._rows)):
                            if self._matrix[r][column] is None:
                                row = r
                                break
                    if row == -1:
                        raise Exception('No remaining place in column %s of table %s to add actor %s' %(column, self, actor))
                    place = (row, column)
                else:
                    raise IndexError('Can not add actor %s in column %s in table %s, table has only %s columns' %(actor, column, self, actor, self._columns))
            else:
                if column < self._columns and row < self._rows:
                    place = (row, column)
                else:
                    if column >= self._columns:
                        raise IndexError('Can not add actor %s in column %s in table %s, table has only %s columns' %(actor, column, self, actor, self._columns))
                    else:
                        raise IndexError('Can not add actor %s in row %s in table %s, table has only %s rows' %(actor, row, self, actor, self._rows))
            # add actor
            if place != (None, None):
                if not expand or keep_ratio:
                    aligner = TableCellAligner(expand=expand, keep_ratio=keep_ratio, align=alignment)
                    aligner.set_element(actor)
                    aligner.set_parent(self)
                    self._matrix[place[0]][place[1]] = aligner
                else:
                    actor.set_parent(self)
                    self._matrix[place[0]][place[1]] = actor
                
        self.queue_relayout()
        
        #for i in range(len(self._rows)):
        #    print 'row %s' %i
        #    for j in range(len(self._columns)):
        #        print '    col %s' %j, self._matrix[i][j]
    
    def set_column_width(self, index, width):
        if index < len(self._columns):
            self._columns[index] = width
        else:
            raise IndexError('Can not set column width in table %s, table has only %s columns' %(self, self._columns))
    
    def set_row_height(self, index, height):
        if index < len(self._rows):
            self._rows[index] = height
        else:
            raise IndexError('Can not set row height in table %s, table has only %s rows' %(self, self._rows))
    
    def do_get_preferred_width(self, for_height=-1):
        preferred_width = (len(self._columns) - 1) * self.spacing
        maximum = 0
        for j in range(len(self._rows)):
            row_width = 0
            for i in range(len(self._columns)):
                actor = self._matrix[j][i]
                if actor is not None:
                    row_width += actor.get_preferred_width(for_height=-1)[1]
            maximum = max(maximum, row_width)
        preferred_width += maximum
        return preferred_width, preferred_width

    def do_get_preferred_height(self, for_width=-1):
        preferred_height = (len(self._rows) - 1) * self.spacing
        maximum = 0
        for i in range(len(self._columns)):
            column_height = 0
            for j in range(len(self._rows)):
                actor = self._matrix[j][i]
                if actor is not None:
                    column_height += actor.get_preferred_height(for_width=-1)[1]
            maximum = max(maximum, column_height)
        preferred_height += maximum
        return preferred_height, preferred_height
    
    def do_allocate(self, box, flags):
        width = box.x2 - box.x1
        height = box.y2 - box.y1
        inner_width = width - 2*self.margin - 2*self.padding
        inner_height = height - 2*self.margin - 2*self.padding
        
        columns_widths = [0 for k in range(len(self._columns))]
        rows_heights = [0 for k in range(len(self._rows))]
        
        # find columns widths
        total_width = 0
        for j in range(len(self._columns)):
            if isinstance(self._columns[j], int):
                columns_widths[j] = self._columns[j]
            else:
                column_width = 0
                for i in range(len(self._rows)):
                    actor = self._matrix[i][j]
                    if actor is not None:
                        column_width = max(column_width, actor.get_preferred_width(for_height=-1)[1])
                columns_widths[j] = column_width
            total_width += columns_widths[j]
        remaining_width = inner_width - total_width - ((len(self._columns) - 1) * self.spacing)
        # find rows heights
        total_height = 0
        for i in range(len(self._rows)):
            if isinstance(self._rows[i], int):
                rows_heights[i] = self._rows[i]
            else:
                row_height = 0
                for j in range(len(self._columns)):
                    actor = self._matrix[i][j]
                    if actor is not None:
                        row_height = max(row_height, actor.get_preferred_height(for_width=-1)[1])
                rows_heights[i] = row_height
            total_height += rows_heights[i]
        remaining_height = inner_height - total_height - ((len(self._rows) - 1) * self.spacing)
        
        # adjust columns widths if some space is remaining
        if remaining_width > 0:
            auto_count = 0
            for j in range(len(self._columns)):
                if not isinstance(self._columns[j], int):
                    auto_count += 1
            if auto_count > 0:
                width_per_column = int(remaining_width / auto_count)
                for j in range(len(self._columns)):
                    if not isinstance(self._columns[j], int):
                        columns_widths[j] += width_per_column
        # adjust rows heights if some space is remaining
        if remaining_height > 0:
            auto_count = 0
            for j in range(len(self._rows)):
                if not isinstance(self._rows[j], int):
                    auto_count += 1
            if auto_count > 0:
                height_per_row = int(remaining_height / auto_count)
                for j in range(len(self._rows)):
                    if not isinstance(self._rows[j], int):
                        rows_heights[j] += height_per_row
        
        base_x = self.margin + self.padding
        base_y = self.margin + self.padding
        x = base_x
        y = base_y
        for i in range(len(self._rows)):
            x = base_x
            for j in range(len(self._columns)):
                actor = self._matrix[i][j]
                if actor is not None:
                    actor_box = clutter.ActorBox(x, y, x + columns_widths[j], y + rows_heights[i])
                    actor.allocate(actor_box, flags)
                    #print x, y, x + columns_widths[j], y + rows_heights[i]
                x += columns_widths[j] + self.spacing
            y += rows_heights[i] + self.spacing
        clutter.Actor.do_allocate(self, box, flags)
    
    def do_foreach(self, func, data=None):
        for i in range(len(self._rows)):
            for j in range(len(self._columns)):
                actor = self._matrix[i][j]
                if actor is not None:
                    func(actor, data)
        
    def do_paint(self):
        for i in range(len(self._rows)):
            for j in range(len(self._columns)):
                actor = self._matrix[i][j]
                if actor is not None:
                    actor.paint()
    
    def do_pick(self, color):
        if self.pick_enabled:
            self.do_paint()
        else:
            clutter.Actor.do_pick(self, color)
    
    def do_destroy(self):
        self.unparent()
        if hasattr(self, '_matrix'):
            for i in range(len(self._rows)):
                for j in range(len(self._columns)):
                    actor = self._matrix[i][j]
                    if actor is not None:
                        actor.unparent()
                        actor.destroy()
                    self._matrix[i][j] = None

#main to test
if __name__ == '__main__':
    stage = clutter.Stage()
    stage.connect('destroy',clutter.main_quit)
    stage.set_size(600, 600)
    stage.set_color((0, 0, 0, 0))
    
    rows = 3
    columns = 3
    table = Table(rows, columns, spacing=20)
    table.set_position(50, 50)
    #table.set_size(500, 500)
    
    for k in range(rows * columns):
        actor = clutter.Rectangle()
        actor.set_size(100, 100)
        actor.set_color((255, 0, 0, 255))
        if k == 4:
            actor.set_size(200, 200)
            table.add(actor, expand=True)
        else:
            table.add(actor)
    
    stage.add(table)
    #print table.get_preferred_size()

    stage.show()
    clutter.main()



