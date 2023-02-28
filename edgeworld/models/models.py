# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class player(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'
    _description = 'Edgeworld player'

    avatar = fields.Image(max_width=200, max_height=200)
    #name = fields.Char(required=True)
    user = fields.Char()
    age = fields.Integer()
    base = fields.One2many('edgeworld.base', 'player')
    is_player = fields.Boolean(default=False)

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
    player = fields.Many2one('res.partner', ondelete="cascade")
    sector = fields.Many2one('edgeworld.sector', ondelete="cascade")
    troop = fields.One2many('edgeworld.troop', 'base')
    building = fields.One2many('edgeworld.building', 'base')
    defense_building = fields.One2many('edgeworld.defense_building', 'base')
    resource_building = fields.One2many('edgeworld.resource_building', 'base')
    troop_capacity = fields.Integer(compute="get_total_troops")
    resource_capacity = fields.Integer(compute="get_total_resources")
    crystal = fields.Integer()
    gas = fields.Integer()
    energy = fields.Integer()
    uranium = fields.Integer()
    base_damage = fields.Integer(compute='get_base_damage')
    base_defense = fields.Integer(compute='get_base_defense')

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

    @api.depends('troop')
    def get_base_damage(self):
        for s in self:
            contador = 0
            for t in s.troop:
                contador += t.damage
            s.base_damage = contador

    @api.depends('defense_building')
    def get_base_defense(self):
        for s in self:
            contador = 0
            for t in s.defense_building:
                contador += t.damage
            s.base_defense = contador

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
    damage = fields.Integer(compute="get_damage")
    health = fields.Integer(compute="get_health")
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

    @api.depends('troop_type', 'level')
    def get_damage(self):
        for s in self:
            contador = 0
            contador += ((s.troop_type.damage*s.level)/5)*s.level
            s.damage = contador

    @api.depends('troop_type', 'level')
    def get_health(self):
        for s in self:
            contador = 0
            contador += ((s.troop_type.health * s.level) / 5) * s.level
            s.health = contador

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
    damage_normalized = fields.Float(compute="get_max_damage", store=True)
    transport_size = fields.Integer()
    troop = fields.One2many('edgeworld.troop', 'troop_type')

    @api.depends('damage')
    def get_max_damage(self):
        contador = max(self.env['edgeworld.troop_type'].search([]).mapped('damage'))
        for record in self:
            if contador != 0:
                record.damage_normalized = record.damage / contador
            else:
                record.damage_normalized = 0


class building(models.Model):
    _name = 'edgeworld.building'
    _description = 'Edgeworld building'
    name = fields.Char(related='building_type.name')
    level = fields.Integer(required=True)
    image = fields.Image(related="building_type.image")
    health = fields.Integer(compute="get_health")
    troop_capacity = fields.Integer(compute="get_troop_capacity")
    stargate_capacity = fields.Integer(compute="get_stargate_capacity")
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

    @api.depends('building_type', 'level')
    def get_health(self):
        for s in self:
            contador = 0
            contador += ((s.building_type.health * s.level) / 5) * s.level
            s.health = contador

    @api.depends('building_type', 'level')
    def get_troop_capacity(self):
        for s in self:
            s.troop_capacity = 0
            if s.building_type.name == "Staging Area":
                contador = 0
                contador += ((s.building_type.troop_capacity * s.level) / 5) * s.level
                s.troop_capacity = contador

    @api.depends('building_type', 'level')
    def get_stargate_capacity(self):
        for s in self:
            s.stargate_capacity = 0
            if s.building_type.name == "Stargate":
                contador = 0
                contador += ((s.building_type.stargate_capacity * s.level) / 5) * s.level
                s.stargate_capacity = contador

    def level_up_building(self):
        for s in self:
            s.level += 1

    def level_down_building(self):
        for s in self:
            s.level -= 1

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
    damage = fields.Integer(compute="get_damage")
    health = fields.Integer(compute="get_health")
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

    @api.depends('defense_building_type', 'level')
    def get_damage(self):
        for s in self:
            contador = 0
            contador += ((s.defense_building_type.damage * s.level) / 5) * s.level
            s.damage = contador

    @api.depends('defense_building_type', 'level')
    def get_health(self):
        for s in self:
            contador = 0
            contador += ((s.defense_building_type.health * s.level) / 5) * s.level
            s.health = contador

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
    health = fields.Integer(compute="get_health")
    resource_capacity = fields.Integer(compute="get_resource_capacity")
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

    @api.depends('resource_building_type', 'level')
    def get_health(self):
        for s in self:
            contador = 0
            contador += ((s.resource_building_type.health * s.level) / 5) * s.level
            s.health = contador

    @api.depends('resource_building_type', 'level')
    def get_resource_capacity(self):
        for s in self:
            s.resource_capacity = 0
            if s.resource_building_type.name == "Supply Depot":
                contador = 0
                contador += ((s.resource_building_type.resource_capacity * s.level) / 5) * s.level
                s.resource_capacity = contador

    def level_up_resource_building(self):
        for s in self:
            s.level += 1

    def level_down_resource_building(self):
        for s in self:
            s.level -= 1

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
    has_passed = fields.Boolean(default=False)
    def update_battles(self):
        print(self.search([]))
        for s in self.search([]):
            if s.date < fields.Datetime.now():
                if s.has_passed == False:
                    if s.base1.base_damage > s.base2.base_defense:
                        if (s.base2.crystal > 100):
                            s.base1.crystal += 100
                            s.base2.crystal -= 100
                        else:
                            s.base1.crystal += s.base2.crystal
                            s.base2.crystal = 0
                        if (s.base2.gas > 100):
                            s.base1.gas += 100
                            s.base2.gas -= 100
                        else:
                            s.base1.gas += s.base2.gas
                            s.base2.gas = 0
                        if (s.base2.energy > 100):
                            s.base1.energy += 100
                            s.base2.energy -= 100
                        else:
                            s.base1.energy += s.base2.energy
                            s.base2.energy = 0
                        if (s.base2.uranium > 100):
                            s.base1.uranium += 100
                            s.base2.uranium -= 100
                        else:
                            s.base1.uranium += s.base2.uranium
                            s.base2.uranium = 0

                        s.has_passed = True

                    else:
                        if (s.base1.crystal > 100):
                            s.base2.crystal += 100
                            s.base1.crystal -= 100
                        else:
                            s.base2.crystal += s.base1.crystal
                            s.base1.crystal = 0
                        if (s.base1.gas > 100):
                            s.base2.gas += 100
                            s.base1.gas -= 100
                        else:
                            s.base2.gas += s.base1.gas
                            s.base1.gas = 0
                        if (s.base1.energy > 100):
                            s.base2.energy += 100
                            s.base1.energy -= 100
                        else:
                            s.base2.energy += s.base1.energy
                            s.base1.energy = 0
                        if (s.base1.uranium > 100):
                            s.base2.uranium += 100
                            s.base1.uranium -= 100
                        else:
                            s.base2.uranium += s.base1.uranium
                            s.base1.uranium = 0

                        s.has_passed = True


class player_wizard(models.TransientModel):
    _name = 'edgeworld.player_wizard'
    _description = 'Wizard per crear players'

    def _default_client(self):
        return self.env['res.partner'].browse(self._context.get('active_id'))  # El context conté, entre altre coses,
        # el active_id del model que està obert.

    avatar = fields.Image(max_width=200, max_height=200)
    name = fields.Many2one('res.partner', default=_default_client, required=True)
    # name = fields.Char(required=True)
    user = fields.Char()
    age = fields.Integer()

    def create_player(self):
        self.ensure_one()
        self.name.write({'user': self.user,
                         'age':self.age,
                         'avatar': self.avatar,
                         'is_player': True
                         })

class battle_wizard(models.TransientModel):
    _name = 'edgeworld.battle_wizard'
    _description = 'Battle wizard'

    state = fields.Selection([('1', 'Select base1'), ('2', 'Select base2'), ('3', 'Resume')], default='1')
    name = fields.Char(default='battle')
    base1 = fields.Many2one('edgeworld.base', ondelete="cascade")
    base2 = fields.Many2one('edgeworld.base', ondelete="cascade")
    date = fields.Datetime(default=fields.Datetime.now)

    def action_previous(self):
        if self.state == '2':
            self.state = '1'
        elif self.state == '3':
            self.state = '2'
        return {
            'name': 'Create Battle',
            'type': 'ir.actions.act_window',
            'res_model': 'edgeworld.battle_wizard',
            'view_mode': 'form',
            'target': 'new',
            'res_id': self.id
        }

    def action_next(self):
        if self.state == '1':
            if len(self.base1) < 1:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'message': 'Base 1 have to be chosen',
                        'type': 'danger',
                        'sticky': False,
                    }
                }
            self.state = '2'
        elif self.state == '2':
            if len(self.base2) < 1:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'message': 'Base2 have to be chosen',
                        'type': 'danger',
                        'sticky': False,
                    }
                }
            else:
                self.state = '3'
        return {
            'name': 'Create Battle',
            'type': 'ir.actions.act_window',
            'res_model': 'edgeworld.battle_wizard',
            'view_mode': 'form',
            'target': 'new',
            'res_id': self.id,
            'context': dict(self._context, base1_context=self.base1.id),
        }

    def create_battle(self):
        self.env['edgeworld.battles'].create({
                    "base1": self.base1.id,
                    "base2": self.base2.id,
                    "name": self.name,
                    "date": self.date
                })

        return {
            'name': 'Create Battle',
            'type': 'ir.actions.act_window',
            'res_model': 'edgeworld.battles',
            'view_mode': 'form',
            'target': 'new',
            'res_id': self.id
        }

class troop_wizard(models.TransientModel):
    _name = 'edgeworld.troop_wizard'
    _description = 'Troop wizard'

    state = fields.Selection([('1', 'Select troop')] , default='1')
    name = fields.Char(related='troop_type.name')
    level = fields.Integer(required=True)
    image = fields.Image(related="troop_type.image")
    damage = fields.Integer(related="troop_type.damage")
    health = fields.Integer(related="troop_type.health")
    troop_type = fields.Many2one('edgeworld.troop_type')
    base = fields.Many2one('edgeworld.base', ondelete="cascade")

    def create_troop(self):

        self.env['edgeworld.troop'].create({
                    "name": self.name,
                    "level": self.level,
                    "image": self.image,
                    "damage": self.damage,
                    "health": self.health,
                    "troop_type": self.troop_type.id,
                    "base": self._context.get('active_id')

                })

        return {
            'name': 'Create Troop',
            'type': 'ir.actions.act_window',
            'res_model': 'edgeworld.troop',
            'view_mode': 'form',
            'target': 'current',
            'res_id': self.id
        }

class building_wizard(models.TransientModel):
    _name = 'edgeworld.building_wizard'
    _description = 'Building wizard'

    state = fields.Selection([('1', 'Select building')] , default='1')
    name = fields.Char(related='building_type.name')
    level = fields.Integer(required=True)
    image = fields.Image(related="building_type.image")
    troop_capacity = fields.Integer(computed="get_troop_capacity")
    building_type = fields.Many2one('edgeworld.building_type')
    base = fields.Many2one('edgeworld.base', ondelete="cascade")
    def create_building(self):
        self.env['edgeworld.building'].create({
                    "name": self.name,
                    "level": self.level,
                    "image": self.image,
                    "troop_capacity": self.troop_capacity,
                    "building_type": self.building_type.id,
                    "base": self._context.get('active_id')

                })

        return {
            'name': 'Create Building',
            'type': 'ir.actions.act_window',
            'res_model': 'edgeworld.building',
            'view_mode': 'form',
            'target': 'current',
            'res_id': self.id
        }

class defense_building_wizard(models.TransientModel):
    _name = 'edgeworld.defense_building_wizard'
    _description = 'Defense building wizard'

    state = fields.Selection([('1', 'Select defense building')] , default='1')
    name = fields.Char(related='defense_building_type.name')
    level = fields.Integer(required=True)
    image = fields.Image(related="defense_building_type.image")
    damage = fields.Integer(related="defense_building_type.damage")
    defense_building_type = fields.Many2one('edgeworld.defense_building_type')
    base = fields.Many2one('edgeworld.base', ondelete="cascade")
    def create_defense_building(self):
        self.env['edgeworld.defense_building'].create({
                    "name": self.name,
                    "level": self.level,
                    "image": self.image,
                    "damage": self.damage,
                    "defense_building_type": self.defense_building_type.id,
                    "base": self._context.get('active_id')

                })

        return {
            'name': 'Create Defense Building',
            'type': 'ir.actions.act_window',
            'res_model': 'edgeworld.defense_building',
            'view_mode': 'form',
            'target': 'current',
            'res_id': self.id
        }

class resource_building_wizard(models.TransientModel):
    _name = 'edgeworld.resource_building_wizard'
    _description = 'Resource building wizard'

    state = fields.Selection([('1', 'Select resource building')] , default='1')
    name = fields.Char(related='resource_building_type.name')
    level = fields.Integer(required=True)
    image = fields.Image(related="resource_building_type.image")
    resource_capacity = fields.Integer(computed="get_resource_capacity")
    resource_building_type = fields.Many2one('edgeworld.resource_building_type')
    base = fields.Many2one('edgeworld.base', ondelete="cascade")
    def create_resource_building(self):
        self.env['edgeworld.resource_building'].create({
                    "name": self.name,
                    "level": self.level,
                    "image": self.image,
                    "resource_capacity": self.resource_capacity,
                    "resource_building_type": self.resource_building_type.id,
                    "base": self._context.get('active_id')

                })

        return {
            'name': 'Create Resource Building',
            'type': 'ir.actions.act_window',
            'res_model': 'edgeworld.resource_building',
            'view_mode': 'form',
            'target': 'current',
            'res_id': self.id
        }