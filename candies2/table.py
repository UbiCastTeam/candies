#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gobject
import clutter
import common
from aligner import Aligner

class TableCellAligner(Aligner):
    __gtype_name__ = 'TableCellAligner'
    
    def __init__(self, **args):
        Aligner.__init__(self, **args)

class Table(clutter.Actor, clutter.Container):
    __gtype_name__ = 'Table'
    """
    A container which presents actors in a table layout
    
    rows/columns can be a list with the size of each row/column
    
    Warning:
        This container uses TableCellAligner to manage actor alignment,
        then the actor's parent is not always the table
    """
    def __init__(self, rows=0, columns=0, margin=0, padding=0, spacing=0, pick_enabled=True):
        clutter.Actor.__init__(self)
        self._margin = common.Margin(margin)
        self._padding = common.Padding(padding)
        self._spacing = common.Spacing(spacing)
        self.pick_enabled = pick_enabled
        
        if isinstance(rows, int):
            self._rows = ['auto' for i in range(rows)]
        elif isinstance(rows, list):
            self._rows = rows
        else:
            raise TypeError('Columns type must be int or list')
        if isinstance(columns, int):
            self._columns = ['auto' for i in range(columns)]
        elif isinstance(columns, list):
            self._columns = columns
        else:
            raise TypeError('Columns type must be int or list')
        self._size = len(self._columns) * len(self._rows)
        self._matrix = [[None for i in range(len(self._columns))] for i in range(len(self._rows))]
    
    def add(self, actor, row=-1, column=-1, align='center', expand=False, keep_ratio=False):
        if actor.get_parent() != self:
            place = (None, None)
            if row == -1 and column == -1:
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
            elif row != -1 and column == -1:
                if row < len(self._rows):
                    for c in range(len(self._columns)):
                        if self._matrix[row][c] is None:
                            column = c
                            break
                    place = (row, column)
                else:
                    raise IndexError('Can not add actor %s in row %s in table %s, table has only %s rows' %(actor, row, self, len(self._rows)))
            elif row == -1 and column != -1:
                if column < len(self._columns):
                    for r in range(len(self._rows)):
                        if self._matrix[r][column] is None:
                            row = r
                            break
                    place = (row, column)
                else:
                    raise IndexError('Can not add actor %s in column %s in table %s, table has only %s columns' %(actor, column, self, len(self._columns)))
            else:
                if column < len(self._columns) and row < len(self._rows):
                    place = (row, column)
                else:
                    if column >= len(self._columns):
                        raise IndexError('Can not add actor %s in column %s in table %s, table has only %s columns' %(actor, column, self, len(self._columns)))
                    else:
                        raise IndexError('Can not add actor %s in row %s in table %s, table has only %s rows' %(actor, row, self, len(self._rows)))
            # add actor
            if place != (None, None):
                if self._matrix[place[0]][place[1]] is not None:
                    self._matrix[place[0]][place[1]].unparent()
                    self._matrix[place[0]][place[1]] = None
                if not expand or keep_ratio:
                    aligner = TableCellAligner(expand=expand, keep_ratio=keep_ratio, align=align)
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
    
    def get_actor(self, row=-1, column=-1):
        if column >= len(self._columns):
            raise IndexError('Can get actor of column %s in table %s, table has only %s columns' %(column, self, self._columns))
        if row >= len(self._rows):
            raise IndexError('Can get actor of row %s in table %s, table has only %s rows' %(row, self, self._rows))
        for r in range(len(self._rows)):
            for c in range(len(self._columns)):
                if isinstance(self._matrix[r][c], TableCellAligner):
                    actor = self._matrix[r][c].get_element()
                else:
                    actor = self._matrix[r][c]
        return actor
    
    def clear_cell(self, row=-1, column=-1):
        actor = self.get_actor(row, column)
        self.do_remove(actor)
    
    def remove(self, actor):
        self.do_remove(actor)
    
    def do_remove(self, actor):
        removed = False
        for r in range(len(self._rows)):
            for c in range(len(self._columns)):
                if self._matrix[r][c] == actor:
                    actor.unparent()
                    self._matrix[r][c] = None
                    removed = True
                    break
                elif isinstance(self._matrix[r][c], TableCellAligner) and self._matrix[r][c].get_element() == actor:
                    self._matrix[r][c].remove_element()
                    self._matrix[r][c].destroy()
                    self._matrix[r][c] = None
                    removed = True
                    break
            if removed:
                break
        self.queue_relayout()
    
    def insert_row(self, index, height='auto'):
        self._rows.insert(index, height)
        self._matrix.insert(index, [None for i in range(len(self._columns))])
    
    def add_row(self, height='auto'):
        self._rows.append(height)
        self._matrix.append([None for i in range(len(self._columns))])
    
    def insert_column(self, index, width='auto'):
        self._columns.insert(index, width)
        for i in range(len(self._rows)):
            self._matrix[i].insert(index, None)
    
    def add_column(self, width='auto'):
        self._columns.append(width)
        for i in range(len(self._rows)):
            self._matrix[i].append(None)
    
    def set_row_height(self, index, height):
        if index < len(self._rows):
            self._rows[index] = height
            self.queue_relayout()
        else:
            raise IndexError('Can not set row height in table %s, table has only %s rows' %(self, self._rows))
    
    def set_column_width(self, index, width):
        if index < len(self._columns):
            self._columns[index] = width
            self.queue_relayout()
        else:
            raise IndexError('Can not set column width in table %s, table has only %s columns' %(self, self._columns))
    
    def do_get_preferred_width(self, for_height=-1):
        preferred_width = (len(self._columns) - 1) * self._spacing.x + 2*self._margin.x - 2*self._padding.x
        for j in range(len(self._columns)):
            column_width = 0
            for i in range(len(self._rows)):
                actor = self._matrix[i][j]
                if actor is not None:
                    column_width = max(column_width, actor.get_preferred_width(for_height=-1)[1])
            preferred_width += column_width
        #print preferred_width
        return preferred_width, preferred_width

    def do_get_preferred_height(self, for_width=-1):
        preferred_height = (len(self._rows) - 1) * self._spacing.y + 2*self._margin.y - 2*self._padding.y
        for i in range(len(self._rows)):
            row_height = 0
            for j in range(len(self._columns)):
                actor = self._matrix[i][j]
                if actor is not None:
                    row_height = max(row_height, actor.get_preferred_height(for_width=-1)[1])
            preferred_height += row_height
        #print preferred_height
        return preferred_height, preferred_height
    
    def do_allocate(self, box, flags):
        width = box.x2 - box.x1
        height = box.y2 - box.y1
        inner_width = width - 2*self._margin.x - 2*self._padding.x
        inner_height = height - 2*self._margin.y - 2*self._padding.y
        
        columns_widths = [0 for k in range(len(self._columns))]
        rows_heights = [0 for k in range(len(self._rows))]
        
        # find columns widths
        total_width = 0
        for j in range(len(self._columns)):
            if total_width != 0:
                total_width += self._spacing.x
            if isinstance(self._columns[j], int):
                columns_widths[j] = self._columns[j]
            else:
                column_width = 0
                for i in range(len(self._rows)):
                    actor = self._matrix[i][j]
                    if actor is not None:
                        column_width = max(column_width, actor.get_preferred_width(for_height=-1)[1])
                columns_widths[j] = column_width
            if inner_width - total_width - columns_widths[j] < 0:
                columns_widths[j] = inner_width - total_width
            total_width += columns_widths[j]
        remaining_width = inner_width - total_width
        # adjust columns widths if some space is remaining
        if remaining_width > 0:
            col_to_expand = None
            auto_count = 0
            for j in range(len(self._columns)):
                if self._columns[j] == 'auto':
                    auto_count += 1
                elif self._columns[j] == 'expand':
                    col_to_expand = j
                    break
            if col_to_expand:
                columns_widths[j] += remaining_width
            elif auto_count > 0:
                width_per_column = int(remaining_width / auto_count)
                for j in range(len(self._columns)):
                    if not isinstance(self._columns[j], int):
                        columns_widths[j] += width_per_column
        
        # find rows heights
        total_height = 0
        for i in range(len(self._rows)):
            if total_height != 0:
                total_height += self._spacing.y
            if isinstance(self._rows[i], int):
                rows_heights[i] = self._rows[i]
            else:
                row_height = 0
                for j in range(len(self._columns)):
                    actor = self._matrix[i][j]
                    if actor is not None:
                        row_height = max(row_height, actor.get_preferred_height(for_width=columns_widths[j])[1])
                rows_heights[i] = row_height
            if inner_height - total_height - rows_heights[i] < 0:
                rows_heights[i] = inner_height - total_height
            total_height += rows_heights[i]
        remaining_height = inner_height - total_height
        # adjust rows heights if some space is remaining
        if remaining_height > 0:
            row_to_expand = None
            auto_count = 0
            for j in range(len(self._rows)):
                if self._rows[i] == 'auto':
                    auto_count += 1
                elif self._rows[i] == 'expand':
                    row_to_expand = j
                    break
            if row_to_expand:
                rows_heights[i] += remaining_height
            if auto_count > 0:
                height_per_row = int(remaining_height / auto_count)
                for j in range(len(self._rows)):
                    if not isinstance(self._rows[j], int):
                        rows_heights[j] += height_per_row
        
        base_x = self._margin.x + self._padding.x
        base_y = self._margin.y + self._padding.y
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
                x += columns_widths[j] + self._spacing.x
            y += rows_heights[i] + self._spacing.y
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
    table = Table(rows, columns, margin=(20, 0))
    table.set_size(600, 600)
    
    for k in range(rows * columns):
        actor = clutter.Rectangle()
        actor.set_size(100, 100)
        actor.set_color((255, 0, 0, 255))
        if k == 0:
            table.add(actor, align='top_left')
        elif k == 4:
            actor.set_size(200, 200)
            table.add(actor, expand=True)
        elif k == 8:
            table.add(actor, align='bottom_right')
        else:
            table.add(actor)
    
    stage.add(table)
    #print table.get_preferred_size()
    
    table.remove(actor)
    #table.destroy()

    stage.show()
    clutter.main()



