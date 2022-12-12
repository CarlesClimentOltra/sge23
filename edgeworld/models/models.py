# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class player(models.Model):
    _name = 'edgeworld.player'
    _description = 'Edgeworld player'
    avatar = fields.Image(max_width=200, max_height=200)
    name = fields.Char(required=True)
    user = fields.Char(required=True)
    age = fields.Integer()
    base = fields.One2many('edgeworld.base', 'player')

class sector(models.Model):
    _name = 'edgeworld.sector'
    _description = 'Edgeworld sector'
    name = fields.Char(required=True)
    population = fields.Selection([('1', 'Very high'), ('2', 'High'), ('3', 'Medium'), ('4', 'Low'), ('5', 'Very low')])
    base = fields.One2many('edgeworld.base', 'sector')

class base(models.Model):
    _name = 'edgeworld.base'
    _description = 'Edgeworld base'
    name = fields.Char(required=True)
    level = fields.Integer(required=True)
    player = fields.Many2one('edgeworld.player', ondelete="cascade")
    sector = fields.Many2one('edgeworld.sector', ondelete="cascade")
    troop = fields.One2many('edgeworld.troop', 'base')
    building = fields.One2many('edgeworld.building', 'base')
    defense_building = fields.One2many('edgeworld.defense_building', 'base')
    resource_building = fields.One2many('edgeworld.resource_building', 'base')
    troop_capacity = fields.Integer(compute="get_total_troops")
    resource_capacity = fields.Integer(compute='get_total_resources')
    crystal = fields.Integer()
    gas = fields.Integer()
    energy = fields.Integer()
    uranium = fields.Integer()

    def level_up_base(self):
        for s in self:
            lvl = (s.level + 1)
            s.write({'level':lvl})

    def level_down_base(self):
        for s in self:
            lvl = (s.level - 1)
            s.write({'level':lvl})

    @api.constrains('crystal')
    def check_level_max(self):
        for b in self:
            if b.crystal > b.resource_capacity:
                raise ValidationError("You have reached the maximum resource capacity")

    @api.constrains('gas')
    def check_level_max(self):
        for b in self:
            if b.crystal > b.resource_capacity:
                raise ValidationError("You have reached the maximum resource capacity")

    @api.constrains('energy')
    def check_level_max(self):
        for b in self:
            if b.crystal > b.resource_capacity:
                raise ValidationError("You have reached the maximum resource capacity")

    @api.constrains('uranium')
    def check_level_max(self):
        for b in self:
            if b.crystal > b.resource_capacity:
                raise ValidationError("You have reached the maximum resource capacity")

    @api.depends('resource_building')
    def get_total_resources(self):
        for s in self:
            contador = 0
            for p in s.resource_building:
                contador += p.resource_capacity
            s.resource_capacity = contador

    @api.depends('building')
    def get_total_troops(self):
        for s in self:
            contador = 0
            for p in s.building:
                contador += p.troop_capacity
            s.troop_capacity = contador

    @api.model
    def update_resources(self):
        for s in self.search([]):
            if s.crystal < s.resource_capacity:
                rec = (s.crystal + 12)
                s.write({'crystal': rec})
            if s.gas < s.resource_capacity:
                rec = (s.gas + 12)
                s.write({'gas': rec})
            if s.energy < s.resource_capacity:
                rec = (s.energy + 12)
                s.write({'energy': rec})
            if s.uranium < s.resource_capacity:
                rec = (s.uranium + 12)
                s.write({'uranium': rec})

class troop(models.Model):
    _name = 'edgeworld.troop'
    _description = 'Edgeworld troop'
    name = fields.Char(related='troop_type.name')
    level = fields.Integer(required=True)
    image = fields.Image(related="troop_type.image")
    troop_type = fields.Many2one('edgeworld.troop_type')
    base = fields.Many2one('edgeworld.base', ondelete="cascade")

    @api.constrains('level')
    def check_level_max(self):
        for b in self:
            if b.level > 22:
                raise ValidationError("Level cant be more than 22")

    @api.constrains('level')
    def check_level_min(self):
        for b in self:
            if b.level < 1:
                raise ValidationError("Level cant be more than 1")

    def level_up_troop(self):
        for s in self:
            s.level += 1

    def level_down_troop(self):
        for s in self:
            s.level -= 1

    @api.onchange('level')
    def _onchange_level(self):
        if self.level < 1:
            return {
                'warning': {
                    'title': "Incorrect 'level' value",
                    'message': "The level cannot be less than 1",
                }, }

        if self.level > 22:
            return {
                'warning': {
                    'title': "Incorrect 'level' value",
                    'message': "TThe level cannot be higher than 22",
                }, }

class troop_type(models.Model):
    _name = 'edgeworld.troop_type'
    _description = 'Troop type'
    image = fields.Image(max_width=200, max_height=200)
    name = fields.Char()
    health = fields.Integer()
    damage = fields.Integer()
    transport_size = fields.Integer()
    troop = fields.One2many('edgeworld.troop', 'troop_type')

class building(models.Model):
    _name = 'edgeworld.building'
    _description = 'Edgeworld building'
    name = fields.Char(related='building_type.name')
    level = fields.Integer(required=True)
    image = fields.Image(related="building_type.image")
    troop_capacity = fields.Integer(computed="get_troop_capacity")
    building_type = fields.Many2one('edgeworld.building_type')
    base = fields.Many2one('edgeworld.base', ondelete="cascade")

    @api.constrains('level')
    def check_level_max(self):
        for b in self:
            if b.level > 22:
                raise ValidationError("Level cant be more than 22")

    @api.constrains('level')
    def check_level_min(self):
        for b in self:
            if b.level < 1:
                raise ValidationError("Level cant be more than 1")

    def level_up_building(self):
        for s in self:
            s.level += 1
            s.troop_capacity = s.level * 50

    def level_down_building(self):
        for s in self:
            s.level -= 1
            s.troop_capacity = s.level * 50

    @api.depends('level')
    def get_troop_capacity(self):
        for s in self:
            s.troop_capacity = s.level * 50

    @api.onchange('level')
    def _onchange_level(self):
        for s in self:
            if self.level < 1:
                return {
                    'warning': {
                        'title': "Incorrect 'level' value",
                        'message': "The level cannot be less than 1",
                    }, }

            if self.level > 22:
                return {
                    'warning': {
                        'title': "Incorrect 'level' value",
                        'message': "TThe level cannot be higher than 22",
                    }, }

            s.troop_capacity = s.level * 50

class building_type(models.Model):
    _name = 'edgeworld.building_type'
    _description = 'Building type'
    image = fields.Image(max_width=200, max_height=200)
    name = fields.Char()
    health = fields.Integer()
    troop_capacity = fields.Integer()
    stargate_capacity = fields.Integer()
    building = fields.One2many('edgeworld.building', 'building_type')

class defense_building(models.Model):
    _name = 'edgeworld.defense_building'
    _description = 'Edgeworld defense building'
    name = fields.Char(related='defense_building_type.name')
    level = fields.Integer(required=True)
    image = fields.Image(related="defense_building_type.image")
    defense_building_type = fields.Many2one('edgeworld.defense_building_type')
    base = fields.Many2one('edgeworld.base', ondelete="cascade")

    @api.constrains('level')
    def check_level_max(self):
        for b in self:
            if b.level > 22:
                raise ValidationError("Level cant be more than 22")

    @api.constrains('level')
    def check_level_min(self):
        for b in self:
            if b.level < 1:
                raise ValidationError("Level cant be more than 1")

    def level_up_defense_building(self):
        for s in self:
            lvl = (s.level + 1)
            s.write({'level':lvl})

    def level_down_defense_building(self):
        for s in self:
            lvl = (s.level - 1)
            s.write({'level':lvl})

    @api.onchange('level')
    def _onchange_level(self):
        if self.level < 1:
            return {
                'warning': {
                    'title': "Incorrect 'level' value",
                    'message': "The level cannot be less than 1",
                }, }

        if self.level > 22:
            return {
                'warning': {
                    'title': "Incorrect 'level' value",
                    'message': "TThe level cannot be higher than 22",
                }, }

class defense_building_type(models.Model):
    _name = 'edgeworld.defense_building_type'
    _description = 'Defense building type'
    image = fields.Image(max_width=200, max_height=200)
    name = fields.Char()
    health = fields.Integer()
    damage = fields.Integer()
    defense_building = fields.One2many('edgeworld.defense_building', 'defense_building_type')

class resource_building(models.Model):
    _name = 'edgeworld.resource_building'
    _description = 'Edgeworld resource building'
    name = fields.Char(related='resource_building_type.name')
    level = fields.Integer(required=True)
    image = fields.Image(related="resource_building_type.image")
    resource_capacity = fields.Integer(computed="get_resource_capacity")
    resource_building_type = fields.Many2one('edgeworld.resource_building_type')
    base = fields.Many2one('edgeworld.base', ondelete="cascade")

    @api.constrains('level')
    def check_level_max(self):
        for b in self:
            if b.level > 22:
                raise ValidationError("Level cant be more than 22")

    @api.constrains('level')
    def check_level_min(self):
        for b in self:
            if b.level < 1:
                raise ValidationError("Level cant be more than 1")

    def level_up_resource_building(self):
        for s in self:
            s.level += 1
            s.resource_capacity = s.level*3000

    def level_down_resource_building(self):
        for s in self:
            s.level -= 1
            s.resource_capacity = s.level*3000

    @api.depends('level')
    def get_resource_capacity(self):
        for s in self:
            s.resource_capacity = s.level*3000

    @api.onchange('level')
    def _onchange_level(self):
        for s in self:
            if self.level < 1:
                return {
                    'warning': {
                        'title': "Incorrect 'level' value",
                        'message': "The level cannot be less than 1",
                    }, }

            if self.level > 22:
                return {
                    'warning': {
                        'title': "Incorrect 'level' value",
                        'message': "TThe level cannot be higher than 22",
                    }, }

            s.resource_capacity = s.level*3000



class resource_building_type(models.Model):
    _name = 'edgeworld.resource_building_type'
    _description = 'Resource building type'
    image = fields.Image(max_width=200, max_height=200)
    name = fields.Char()
    health = fields.Integer()
    resource_capacity = fields.Integer()
    hourly_rate = fields.Integer()
    resource_building = fields.One2many('edgeworld.resource_building', 'resource_building_type')

class battles(models.Model):
    _name = 'edgeworld.battles'
    _description = 'Battles'
    name = fields.Char()
    base1 = fields.Many2one('edgeworld.base', ondelete="cascade")
    base2 = fields.Many2one('edgeworld.base', ondelete="cascade")
    date = fields.Datetime()
    stop = fields.Integer()

